# MedTAG Benchmark 

MedTAG annotation performance has been assessed by means of an automatic agent, which simulated the annotation process for two specific use-cases: 

1. **document-level annotation**: this task concerns the annotation of documents with labels that describe the overall document content.
2. **mention-level annotation**: this task concerns the identification of concept-related mentions, in the documents' textual content.

The annotation process performance has been evaluated in terms of:

1. **number of actions**: number of user-required actions (e.g. clicks and keys pressed) to annotate documents according to the use-cases specified.
2. **time elapsed**: the amount of time required to perform the whole annotation process (i.e. all the sample documents considered get annotated).

The analysis we conducted considers a sample of one hundred documents, randomly chosen from a real dataset concerning the digital pathology domain (i.e. colon cancer clinical reports). We assessed the performances of MedTAG and other annotation tools including [ezTag](https://eztag.bioqrator.org/), [MyMiner](https://myminer.armi.monash.edu.au/) and [tagtog](https://www.tagtog.net/). We measured the number of actions and the time elapsed forty times for each annotation tool, then we computed the mean and the standard deviation. 

The experiment results are summarized in the following table.  