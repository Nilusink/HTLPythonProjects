from multiprocessing import Process, Pipe
"""
Written by 
25.01.2024

This Python program uses multiprocessing to calculate squares for a
specified range of values in parallel.The main function prompts the user
for the start value, end value, and the number of processes.It then
divides the workload among the processes, assigns subsets, and launches
parallel processes to calculate squares.The results are communicated back
to the main program, which prints the calculated squares along with process information.

"""

# worker function doing some stuff
def worker(conn, ... ):
    """
    Worker function for parallel processing.
    Args:conn, ... ?      
    Returns: None 
    """
    conn.send(["test"])
    conn.close()

# main function
if __name__=="__main__":
    """
    Main function to orchestrate the parallel processing.
    Returns: None
    """    
    # get user input 


    # calculate the share of work for each process


    # calculate the subsets


    # start the processes
    for i in range(1):
        pass 
        #parent_conn,child_conn=Pipe()
        #p=Process(...)
        #p.start()
        #print(parent_conn.recv())
        #p.join()
        #parent_conn.close()



