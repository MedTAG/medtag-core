# MedTAG full source code
![medTAG_logo_462x132](/home/fabio/repositories/github/medtag-core/img/screenshots/medTAG_logo_462x132.png)

MedTAG: An open-source biomedical annotation tool for diagnostic reports.

This repository contatins the full source code of MedTAG, a biomedical annotation tool for tagging biomedical concepts in clinical reports.

# Requirements

Since MedTAG is provided as a Docker container, both [docker](https://docs.docker.com/engine/reference/commandline/docker/) and [docker-compose](https://docs.docker.com/compose/) are required. To this aim, check out the [installation procedure](https://docs.docker.com/get-docker/) for your platform. Moreover, the MedTAG docker container instantiates a [PostgreSQL](https://www.postgresql.org/) database, so if you plan to insert a large amount of data make sure you have enough disk space. For what concerns the browser choice, Chrome would be the best browser to work with MedTAG. Nevertheless, both Safari and Firefox are supported as well.




# Installation
If you already have both [docker](https://docs.docker.com/engine/reference/commandline/docker/) and [docker-compose](https://docs.docker.com/compose/) installed on your machine, you can skip the first two steps.

1. Install Docker. To this aim, check out the correct [installation procedure](https://docs.docker.com/get-docker/) for your platform.

2. Install Docker-compose. As in the first step, check out the correct [installation procedure](https://docs.docker.com/compose/install/) to get [docker-compose](https://docs.docker.com/compose/) installed for your platform.

3. Download or clone the [medtag-core](https://github.com/MedTAG/medtag-core) repository.

4. Open the [medtag-core](https://github.com/MedTAG/medtag-core) project folder and, on a new terminal session, type ```docker-compose up```. After running the latter command the installation of MedTAG dependencies is performed and the following output will be generated:

   ![installation_process_output](/home/fabio/repositories/github/medtag-core/img/screenshots/installation_process_output.png)

   5.  MedTAG installation has completed and you can access it on your browser at http://0.0.0.0:8000/.

   **NOTE**: If you want to shut down MedTAG, open a new terminal window and navigate to the project folder. Finally type `docker-compose down`

   **NOTE**: If you want to redo the whole installation process and run MedTAG in *Test Mode* (i.e., with the provided sample data) open a new terminal and, inside the project folder, run the following commands: 

   1. `docker-compose down`
   2. `sudo rm -rf data`
   3. `docker image ls`
   4. Then select the IMAGE ID of the image whose name is *medtag dockerized web* and run: `docker image rm <IMAGE ID>`
   5. Finally run `docker-compose up`

# Getting started

## Test Mode

The following procedure describe how to start using MedTAG in _Test Mode_, which allows you to try MedTAG with the pre-loaded dataset of reports. If you want to load and work with your own reports, you have to proceed with the following steps anyway and then jump to the _Customize MedTAG_ section.

1. Open a new browser window and go to: http://0.0.0.0:8000/, you will see the MedTAG web interface.

2. Log into MedTAG using "Test" both as username and password. In this way, you will enter in MedTAG using the _Test Mode_ that allows you to try MedTAG features using a sample of data we provided.

   ![login_test](/home/fabio/repositories/github/medtag-core/img/screenshots/login_test.png)

3. Once you have logged in, you will be asked to provide a first reports configuration. In particular, you have to provide:

   1. **Language**: this is the language of the reports you will annotate.

   2. **Use case**: this is the use case of the clinical reports (e.g. Colon cancer and Lung cancer).

   3. **Institute**: this is the medical institute which provides the diagnostic reports.

      **NOTE**:  In  _Test Mode_ only one combination is possible (i.e., English, Colon, AOEC )

![initial_test_conf](/home/fabio/repositories/github/medtag-core/img/screenshots/initial_test_conf_2.PNG)

## Customize MedTAG

In order to customize MedTAG with your own data, you need to provide three CSV files (i.e, *reports_file*, *concepts_file*, *labels_file*). Please, **make sure to use a comma as separator** for your CSV files. Furthermore, **make sure to escape values that contains commas**.

### CSV files needed:

- **reports_file**: this file contains the clinical reports to annotate. The csv header must contain the following columns:

  1. **id_report**: the report unique identifier.

  2. **language**: the language adopted for the report textual content.

  3. **institute**: the health-care institute which provides the diagnostic reports.

  4. **usecase**: the report use-case (e.g. colon cancer) indicates the clinical case the report refers to.

     **NOTE**: if you are not interested in providing either the *institute* or the *usecase* you can assign them a default value of your choice, that holds for all the rows of the *reports_file*.

     ![report_file](/home/fabio/repositories/github/medtag-core/img/screenshots/report_file.PNG)

     **NOTE:** In addition to the previous mandatory columns, you need to provide a set of additional columns to describe the actual textual content of your reports (e.g. the diagnosis text, the patient information and so on). You can specify as many columns as you want.

  - **concepts_file**: this file contains the concepts used for annotating the clinical reports. All the concepts must be identified with a *concept_url* which uniquely identifies the concept according to a reference ontology. The csv header must contain the following columns:

  1. **concepts_url**: the URL of the concept in the reference ontology.

  2. **concepts_nome**:  the name of the concept the concept url points to.

  3. **area**: this is a category associated to the concept.

  4. **usecase**: the concept use-case (e.g. colon cancer) indicates the clinical case the concept refers to.

     **NOTE**: if you are not interested in providing either the _area_ or the *usecase* you can assign them a default value of your choice, that holds for all the rows of the *concepts_file*. It is worth noting that the _usecase_ provided for the concepts should be coherent with the one provided for the reports.

     ![concept_file](/home/fabio/repositories/github/medtag-core/img/screenshots/concept_file.PNG)

- **labels_file**: this file contains the labels used for annotating the clinical reports. The labels describe a diagnostic property of a clinical report. For instance,  the "Cancer" label describe the presence of a cancer-related disease. The csv header must contain the following columns:

  1. **label**: the label text.

  2. **usecase**:  the label use-case (e.g. colon cancer) indicates the clinical case the concept refers to.

     **NOTE**: if you are not interested in providing the *usecase* you can assign it a default value of your choice, that holds for all the rows of the _labels_file_.

     ![label_ex](/home/fabio/repositories/github/medtag-core/img/screenshots/label_ex.PNG)

### Data configuration

The following procedure describe how to configure MedTAG in order to load your own reports and work with them in MedTAG. It is worth noting that only the admin user has the privileges to change the MedTAG configurations. Moreover, **every time a new configuration is provided the previous one will be overwritten, thus data and annotations will be removed as well**.   

To start a new configuration follow the instructions below:

1. Open the Menu from the _Test Mode_ and go to _Configure_.

   ![menu_main_interface](/home/fabio/repositories/github/medtag-core/img/screenshots/menu_main_interface.PNG)

   ![configure](/home/fabio/repositories/github/medtag-core/img/screenshots/configure.PNG)

2. Read and follow the instructions of the guided procedure.

   ![](/home/fabio/repositories/github/medtag-core/img/screenshots/update_data_conf.png)

3. Provide the CSV files.

   **NOTE**: You can add one or more files from the same folder. If it is the first time you configure MedTAG, you are asked to provide both the username and the password that will be used by the admin user to login into MedTAG. The admin user is the only one who can change the configuration files and access the data. If you do not have access to _Configure_ section (i.e., you do not see it in the side bar), this means that you are not logged in as the admin user.

   **NOTE**: The ***reports_file* is mandatory**. Once you uploaded it, MedTAG automatically detects the columns which characterize your report and asks you to choose which fields of the report you want to hide, display or annotate. **You need to set at least one field to be displayed**.

   **NOTE**: The *concepts_file* and _labels_file_ and are not mandatory. This means that if you are not interested in labels annotation and/or concepts identification you can avoid to provide them. By the way,  you must provide either the _labels_file_ or the *concepts_file* or set at least one field to *Display* and *Annotate*.

   ![reportsfields](/home/fabio/repositories/github/medtag-core/img/screenshots/reportsfields.PNG)

4. Check the format of the provided CSV files, by clicking on the *Check* button. Then, the automatic procedure will produce some state messages in different colors:

     - Green: messages in green color (i.e., success messages)  mean that the provided CSV files are well-formatted.

     - Orange: messages in orange color (i.e., warning messages) mean that you **should revise the format of the provided CSV files**. Nevertheless, the provided CSV files are accepted anyway.

     - Red: messages in red color (i.e., error messages) mean that you **must revise the format of the provided CSV files**, since they are not well-formatted. Error messages provide information about the errors occurred and suggest the user how to fix the issues.

       ![examplemessages](/home/fabio/repositories/github/medtag-core/img/screenshots/examplemessages.PNG)

5. The procedure has ended, a notification of success or error will be provided. In case of successful configuration of MedTAG, the login page will look like the screenshot below. 

   ![loginnew](/home/fabio/repositories/github/medtag-core/img/screenshots/loginnew.PNG)

### Update data configuration

The following procedure describe how to provide additional data to the current configuration of MedTAG. Updating the configuration is possible only if you are not running MedTAG with the sample data we provided, that is, MedTAG is not running in *Test Mode*. In order to update a configuration follow these steps:

1. Open the Menu and go to *Configure* and click on *Update configuration*.

2. Select what you want to update. You can add some reports, labels or concepts. You can also change the fields to display and annotate. If you want to update the fields to annotate and display, remember that you cannot set to *Hide* or *Display* the fields you previously decided to annotate, since this would affect the annotations that rely on those fields.

   **NOTE**: If you decide to add reports having columns that MedTAG has never detected before, you will be asked to choose what columns to display, hide or annotate.

   ![update](/home/fabio/repositories/github/medtag-core/img/screenshots/update.PNG)