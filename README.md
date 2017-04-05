## How to transfer data (using Mac)
1. Open terminal
2. Type in:    
```
sftp SSRL\\b_heimann@specftp.slac.stanford.edu:data/bl7-2/Apr2017
```

then enter password. It is recommended to keep this terminal connected
to SFTP.
   
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
    * If haven't done so, create the folders data/ (for raw data)
    and data\_npz/ (for converted data) by entering in terminal:   
    ```
    mkdir data
    mkdir data_npz
    ```


## How to run the programs
### First do a test scan:
* After finding the primary peak and secondary peak position,
record in logbook and modify the parameters in config file.     
* In config file, make sure that do\_test = yes and other parameters
are correct. Also check file paths. Then generate macro by:   
```
python genmacro.py [config file name]
```
* Use SFTP to transfer the macro to BL7-2 and run it there.  
* The test run must have the same scan parameters as the 2d scan

### Then read data and generate exposure time array:
* Use SFTP to transfer data to data/ folder. Make sure to transfer
all desired .raw and associated .raw.pdi files. It does not matter
whether these data are in subfolders or not.

* Run
```
python convert2npy.py
``` 

This will convert *all* .raw and .raw.pdi file in data/ to .npz files
in data\_npz.

* Modify the "filename" parameter in gettimes.py to match those from
test scan. Then run  
```
python gettimes.py
```
This will generate file times.npy which will be used for 2d scan.


### Generate macro for 2D scan:
* Modify configuration file. Make sure:   
    * mode = 2d
    * do\_test = no
    * Primary scan direction, range, and steps are the same as in 
      test scan
    * Filenames are different from test scan

* Run
```
python genmacro.py [config file name]
```

### Transfer generated macro
* SSRL does not allow us to send files through SFTP. We can either send the
generated macro through email, or upload to Google Drive

* To upload to Google Drive, in the repository, enter for Mac:
```
./gdrive-osx upload -p 0Bz7BBuzs7NtCLXZkOXBfZVhSMW8 [macro file name]
```
for Linux/Unix:
```
./gdrive-linux upload -p 0Bz7BBuzs7NtCLXZkOXBfZVhSMW8 [macro file name]
```
The first time you use the program, you will be prompted
    to enter a confirmation number by looking at a website. Please trust it
    and follow the instructions.
