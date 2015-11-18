# downloads N GDocs files in serial

from gdoc2latex import download_to_file

directory = "compile/chapters/" # compile/ contains LaTeX master doc and .bib

files = [
  ('introduction.tex', 'https://docs.google.com/document/d/1SHho1qONCZ5mvs45FjFo7P__66hZx1D7lnHAUZH-Hyc/edit'),
  ('literature_review.tex', 'https://docs.google.com/document/d/1GP8-kllP8mYJvT7dfmauEVoRHj2AlK7080Sy849l-wY/edit'),
  ('idiums_design.tex', 'https://docs.google.com/document/d/1mF5jaBqpomkBciA5bFzIa-ypgF9qR72uvP7zigzlQJ4/edit'),
  ('simulation.tex', 'https://docs.google.com/document/d/1qEXAWmX-4Bhl4y_JMspO47jMGRIdaqH4-UDEEdFEIc8/edit'),
 # ('thesis_experiment.tex', 'https://docs.google.com/document/d/1Cpqm9inI0Mh1zGLjUyWO4PtWSoYscqACcd7uE3Gj7V4/edit'),
  ('mini-thesis_experiment.tex', 'https://docs.google.com/document/d/1IBWOJc5ywim6Qr6h4NhTWi4ikth1WvxQ-bVl1KExBnk/edit'),
 # ('executive_summary.tex', 'https://docs.google.com/document/d/1OEN_KLOTyltztNmaTsMdd3W9hI8SG8tSMSCc5gBOgC8/edit'),
  ('experiment.tex', 'https://docs.google.com/document/d/1k3v2X4saS-hMBqMk4o9s9xxSLeMCRW07FBSXRhw0_64/edit'),
  ('meta-review.tex', 'https://docs.google.com/document/d/1v-EhKU74HwH0sW4qkZAvv1Uvxcjc_B0luA51iy32VOU/edit'),
  ('conclusion.tex', 'https://docs.google.com/document/d/1mIkdyGgEZrtM-MCKXfjPJKGdK7Tk9Z8yrg2oyAv-4pk/edit'),
  ('future_work.tex', 'https://docs.google.com/document/d/1Bz3Fvo3TvJDW1F5sfys_O_ZUY74E-KkqdcynchsawCU/edit'),
#  ('.tex', ''),
#  ('.tex', ''),
]

for tup in files:
	download_to_file(tup[1],directory+tup[0])
