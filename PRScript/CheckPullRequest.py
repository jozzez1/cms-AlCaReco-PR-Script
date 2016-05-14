#!/usr/bin/env/python
#script that compares some runTheMatrix.py flows produced by the base CMSSW and the pull request

import urllib
import string
import os
import sys
import array
import LaunchOnCondor
import glob
import time
import commands

# 1st argument is the name of the CMSSW release
# 2nd argument is the ref. number of the pull request, e.g. 14406, read it from the browser

CWD       = os.getcwd()
compare   = [
        #dirname #pull #list of workflows for runTheMatrix.py
       ["vanilla", 0, [["1000.0", 5000], ["1001.0", 5000], ["135.4", 5000], ["140.53", 5000], ["4.22", 5000], ["8.0", 5000]]],
       ["changes", 1, [["1000.0", 5000], ["1001.0", 5000], ["135.4", 5000], ["140.53", 5000], ["4.22", 5000], ["8.0", 5000]]],
]

### equivallent to step 0 -- we prepare the terrain
if len(sys.argv) == 3:
   CMSSWREL = sys.argv[1]
   for toCompare in compare:
      os.system("mkdir %s" % toCompare[0])
      os.chdir("%s/%s" % (CWD, toCompare[0]))
      os.system("export SCRAM_ARCH=slc6_amd64_gcc530")
      os.system("scramv1 project %s" % CMSSWREL)
      print "*** Preparing %s ***" % toCompare[0]
      os.chdir("%s/%s/%s/src" % (CWD, toCompare[0], CMSSWREL))
      print "Initializing git repository ..."
      os.system("eval `scramv1 runtime -sh` && git cms-init > ../creation.log 2>&1")
      
      if toCompare[1] == 1:
         print "Applying patch ..."
         os.system("eval `scramv1 runtime -sh` && git cms-merge-topic %s > ../merge.log 2>&1" % sys.argv[2])

      print "Compiling ..."
      os.system("eval `scramv1 runtime -sh` && scramv1 b -j16 > ../compile.log 2>&1")
      
      os.system("mkdir testDir")
      os.chdir(CWD)

elif len(sys.argv) == 2:
   ### submit runTheMatrix workflows to the cluster
   if sys.argv[1] == "1":
      JobName = "AlcaRecoComparison"
      FarmDirectory = "FARM"
      for toCompare in compare:
         CMSSWREL = os.listdir("%s/%s" % (CWD, toCompare[0]))[0]
         os.chdir("%s/%s/%s/src/testDir" % (CWD, toCompare[0], CMSSWREL))
         os.system("eval `scramv1 runtime -sh`")
         LaunchOnCondor.SendCluster_Create(FarmDirectory, JobName)
         for workflow in toCompare[2]:
            LaunchOnCondor.SendCluster_Push (["BASH", "runTheMatrix.py -l %s --command=\"-n %i\"; mv %s* %s/%s/%s/src/testDir/%s/outputs/results_%s" % (workflow[0], workflow[1], workflow[0], CWD, toCompare[0], CMSSWREL, FarmDirectory, workflow[0])]);
            LaunchOnCondor.Jobs_FinalCmds = ["rm runall-report-step123-.log"]
#            LaunchOnCondor.Jobs_FinalCmds = ["mv %s* %s/%s/%s/src/testDir/%s/outputs/" % (workflow[0], CWD, toCompare[0], CMSSWREL, FarmDirectory)]
         os.system("rm -rf %s/%s/%s/src/testDir/%s/outputs/*" % (CWD, toCompare[0], CMSSWREL, FarmDirectory))
         LaunchOnCondor.SendCluster_Submit()
         os.chdir(CWD)

   ### make compare the edmEvents stuff
   elif sys.argv[1] == "2":
      for toCompare in compare:
         print '*** Creating edm reports for %s ***' % toCompare[0]
         CMSSWREL = os.listdir("%s/%s" % (CWD, toCompare[0]))[0]
         os.chdir("%s/%s/%s/src/testDir/FARM/outputs" % (CWD, toCompare[0], CMSSWREL))
         for workflow in toCompare[2]:
            os.system("eval `scramv1 runtime -sh` && find result_%s -name \"*root\" | grep AlCa | xargs -I% edmEventSize -v -a % > eventSizeReport.log 2>%1")
            os.system("eval `scramv1 runtime -sh` && find result_%s -name \"*root\" | grep AlCa | xargs -I% edmDumpEventContent % > eventContentReport.log 2>%1")

   ### compare the plots using validate.C
   elif sys.argv[1] == "3":
      print 'Not finished yet ...'
   
   elif sys.argv[1] == "clean":
      for toCompare in compare:
         os.system ("rm -rf %s" % toCompare[0])
