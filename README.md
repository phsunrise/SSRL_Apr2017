## How to transfer data (using Mac)
1. Open terminal
2. Type in:    
> sftp SSRL\\\\b\_heimann@specftp.slac.stanford.edu   

then enter password   
3. Commands: 

Command | What it does
------- | --------
 pwd    | Print working directory of remote host    
 lpwd   | Print working directory of local client    
 cd     | Change directory on the remote host    
 lcd    | Change directory on the local client    
 ls     | List director on the remote host    
 lls    | List directory on the local client    
 mkdir  | Make directory on remote host    
 lmkdir | Make directory on local client    
 get    | Receive file from remote host to local client    
 put    | Send file from local client to remote host    
 help   | Display help text    

4. Data should be saved in data/ or its subfolders 
    * If haven't done so, create the folders data/
    and data\_npz/ by entering in terminal:   
    > mkdir data/     
    > mkdir data\_npz/


## How to run the programs
### First do a test run:
* After finding the primary peak and secondary peak position,
record in logbook and modify the parameters in config file    
* In config file, make sure that do\_test = yes and other parameters
are correct. Then 
