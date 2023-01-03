# Flow-shop-scheduling-test

This is the project for evaluating scheduling algorithm for Fitfactory scheduler. 

1. <p style="color:#008080">google_ortool_test.py</p> Test the google_ortool on job shop scheduling problem (object function: minimize the makespan).
    
   [https://developers.google.com/optimization/scheduling/job_shop](https://developers.google.com/optimization/scheduling/job_shop).
   
2. <p style="color:#008080">convert_instance.py</p> Convert benchmark instances in txt files into the format that Fitfactory Schedular can import.
   
   Input: *./data/text_instance/* 

   Output: *./data/converted_instances/* 

3.  <p style="color:#008080">priority_schedular.py</p> 
    Priority Schedular reprogramme in python.
    
    Input: *./data/converted_instance/*
    
    Output: *./data/priority_schedular/*

4. <p style="color:#008080">validation_scheular.py</p>
   Compare the difference between the output from priority schedular and Fitfactory schedular.

   Priority Schedular output: *./data/priority_schedular/*

   Fitfactory Schedular output: *./data/FF_schedular/*

5. <p style="color:#008080">schedular_ortool.py</p>
   
   ortool to schedular the benchmark instances

   Input: *./data/test_instances/*

   Output: Gantt Charts. 

