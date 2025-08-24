# cross-matching-for-pulsars
in order to catch these faint pulsars that may be missed during the sifting, ranking, or the candidate selections, we propose a cross matching method to sift pulsar candidates from multiple observations, based only on spin periods and DM values.

# Overview
This Python script is designed to process and analyze pulsar candidates from multiple observations. It identifies faint pulsar signals that appear in multiple observations by cross-matching candidates based on their dispersion measure (DM) values and spin periods.

# Preprocessing Requirements
Before using this cross-matching script, observation files must be preprocessed using PRESTO (PulsaR Exploration and Search TOolkit) to remove interference and de-dispersion：

# Pipeline Flow:
1.RFI Mitigation (rfifind)
2.Dedispersion (prepsubband + DDplan.py, optional)
3.FFT (realfft)
4.Acceleration Search (accelsearch)
5.Candidate Sifting (ACCEL_sift.py)



# Key Features
· Fully based on PRESTO utilities.

· Processes multiple observation files from a specified directory

· Groups candidates based on period similarity (ΔP/P ≤ 1%) and based on DM value similarity (ΔDM/DM ≤ 10%)

· Generates visualizations showing period and DM variations across observations



# Requirements
Python 3.6+
Required libraries:
NumPy
Matplotlib
Collections
