# Readme


This is a small script with which it is easier to compare changes in `CMSSW`. It creates different versions of CMSSW, applies the requested changes, compiles them and then uses the `runTheMatrix.py` to create some samples which are generated at the cluster, using `LaunchOnCondor.py`, written by Loic Quertenmont. After the samples are created, script compares different AlCaReco root files using `edmEventSize` and `edmDumpEventContent`. With the final step it also produces plots using modified version of `validate.C` from the cms-bot.

## Step 0
You should start by editing the `compare` variable. Each element is a list:
```
compare = [["name of the directory with the CMSSW version", "apply the PR or not", "workflowList"]]
workflowList = ["workflow number", "number of events to generate"]
```
It should run out of the box, but in case you have to change the values there, it is best to do it at the very beginning.

Now you are ready to run the script. Set up the `SCRAM_ARCH` environment variable first. It takes two arguments: first is the CMSSW release and second is the pull request number. Example:
```
export SCRAM_ARCH=slc6_amd64_gcc530
python CheckPullRequest.py CMSSW_8_1_X_2016-05-11-1100 14406
```

## Step 1

For this step you need the `LaunchOnCondor.py` script (included in the repository). This will now submit the workflows to the cluster. Results are moved to the `CMSSW_RELEASENUMBER/src/testDir/FARM/outputs` directory.


## Step 2

In this final step we process the results. Programs `edmDumpEventContent` and `edmEventSize` produce logfiles, which you can then compare using `vimdiff` or just `diff`, for plots it will use the `validate.C` from the `cms-bot` repository.
