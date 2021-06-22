# MedTAG Benchmark 

MedTAG annotation performance has been assessed by means of an automatic agent, which simulated the annotation process for two specific use-cases: 

1. **document-level annotation**: this task concerns the annotation of documents with labels that describe the overall document content.
2. **mention-level annotation**: this task concerns the identification of concept-related mentions, in the documents' textual content.

The annotation process performance has been evaluated in terms of:

1. **number of actions**: number of user-required actions (e.g. clicks and keys pressed) to annotate documents according to the use-cases specified.
2. **time elapsed**: the amount of time required to perform the whole annotation process (i.e. all the sample documents considered get annotated).

The analysis we conducted considers a sample of one hundred documents, randomly chosen from a real dataset concerning the digital pathology domain (i.e. colon cancer clinical reports). We assessed the performances of MedTAG and other annotation tools including [ezTag](https://eztag.bioqrator.org/), [MyMiner](https://myminer.armi.monash.edu.au/) and [tagtog](https://www.tagtog.net/). We measured the number of actions and the time elapsed for each annotation tool. We computed the mean and the standard deviation over forty trials.

The experiment results are summarized in the following tables:

**Table 1**: **document-level annotation** performance analysis

|                                            Tool | #Actions | Elapsed time in seconds (mean) | Standard deviation in seconds |
| ----------------------------------------------: | :------: | :----------------------------: | :---------------------------: |
| [MedTAG](https://github.com/MedTAG/medtag-core) |   200    |             46.84              |             0.803             |
|  [MyMiner](https://myminer.armi.monash.edu.au/) |   100    |             56.677             |             0.416             |
|               [tagtog](https://www.tagtog.net/) |   400    |             205.74             |             5.471             |



**Table 2**: **mention-level annotation** performance analysis

|                                            Tool | #Actions | Elapsed time in seconds (mean) | Standard deviation in seconds |
| ----------------------------------------------: | :------: | :----------------------------: | :---------------------------: |
| [MedTAG](https://github.com/MedTAG/medtag-core) |   419    |            159.337             |             0.479             |
|           [ezTag](https://eztag.bioqrator.org/) |   307    |             260.34             |             0.576             |
|               [tagtog](https://www.tagtog.net/) |   404    |            304.692             |            10.067             |



## Technical details 

### Datasets

The datasets considered for the benchmark experiments consist of a sample of one hundred documents from the digital pathology domain (i.e. colon cancer clinical reports anonymized). The datasets are available inside the folder [datasets](https://github.com/MedTAG/medtag-core/tree/main/benchmark/datasets)

### Source code

The benchmark experiments have been conducted using the Python Web automation library [Selenium](https://www.selenium.dev/). The full source code of the automated agents implemented is available inside the folder [automated_agents_selenium](https://github.com/MedTAG/medtag-core/tree/main/benchmark/automated_agents_selenium). 