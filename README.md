# AI Medical Assistant 🤖🏥
An intelligent medical assistant that helps users diagnose symptoms, recommend specialists, and locate nearby healthcare facilities.
## Overview
This project is powered by an AI agent with two key functionalities. First, it performs an initial diagnosis by analyzing not only the provided symptoms but also the patient’s medical history, family history, travel history, and recent epidemic reports from the news. Second, it helps locate nearby medical centers, clinics, and pharmacies based on the given address.
The diagram below provides an overview of the system's workflow, followed by detailed explanations of each AI agent.

<img src="Flowchart.png" width="400"/>

1. **Input Data**
   The input data will be a .csv file containing information on patients' symptoms, medical history, family history, travel history, and address.

3. News Searcher
This AI agent will search for recent news related to epidemics.

4. Initial Diagnosis
This AI agent will analyze the provided symptoms, medical history, family history, and travel history, along with the results from the News Searcher, to     suggest possible diseases.

5. Medical Department Suggestion
Based on the initial diagnosis, this AI agent will recommend the appropriate medical department the user should visit.

6. Search for Nearby Medical Centers and Clinics
Once the medical department has been suggested, this AI agent will connect to external sources to find nearby hospitals based on the provided address.

7. Medication Suggestion
This AI agent will recommend possible medications based on the previous results.

8. Search for Nearby Pharmacies
After the medication suggestion, this AI agent will search for nearby pharmacies based on the provided address.


