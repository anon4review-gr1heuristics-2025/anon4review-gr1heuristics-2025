README for Artifact Evaluation of TACAS 2025 Submission

"Performance Heuristics for GR(1) Realizability Checking and Related Analyses"


===========================
1.   Artifact Contents
===========================


The zip file contains the following files and directories:


1.      test: refer to the "Artifact Evaluation Guide.pdf" file
           
2.      results: this directory contains the csv results

	2.1	memoryless: this directory contains CSV files with the results for the "Partial memoryless vs. Spectra" row in Table 1
	2.2	ordering: this directory contains CSV files with the results for the "Static variable ordering vs. partial memoryless" and "Justice ordering vs. partial memoryless" in Table 1
	2.3	sfa: this directory contains CSV files with the results for the "Simp. auto. + aux. grp. vs. partial memoryless" in Table 1
	2.4	alg_reduction: this directory contains CSV files with the results for "WS vs. part. mem." and "Inh. vac. vs. part. mem." rows in Table 1
	2.5	final: this directory contains CSV files with the results for the rows of Table 2

3.      data: this directory contains the datasets and the filtering scripts

    	3.1 	all the datasets where each is in one folder
	3.2 	all the datasets where each is in the original subfolders structure
	3.3 	scripts that enable the filtering

4.	analysis: this directory contains the Python code for filling the results tables in the evaluation section


======================================
2.    Run Configurations
======================================


Due to the use of multiple heuristics, their combinations and variants, we used a modular experiment framework.
A configuration allows the adjustment and combination of every setting for an experiment.
For a comprehensive description of the config structure refer to the "Artifact Evaluation Guide.pdf" file.
To run a config it is necessary to place it inside the CONFIGS directory and select it in the config selection step in 3.


===========================
3.    Results Format
===========================


The contents of a csv result file is a table with the measurement data. Each row represents the data for a single run.


The columns of a csv result file include:


	3.1 	Spec: name of the specification
	3.2 	RunConfig: the config used
	3.3 	ActionType: the type of work performed
	3.4 	Result: the result of the work. For example, for REALIZABILITY, the two possible values are SYS_REAL and SYS_UNREAL
	3.5 	TOTAL_TIME: the total time of the run, in milliseconds


===========================
4.    How to Run
===========================


Section 6 in the "Artifact Evaluation Guide.pdf" file contains the guide of how to run an experiment, including an example run.