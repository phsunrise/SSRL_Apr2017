## How to transfer data (using Mac):
1. Open terminal
2. Type in:
    sftp SSRL\\b_heimann@specftp.slac.stanford.edu
then enter password
3. Commands: 
pwd     Print working directory of remote host
lpwd    Print working directory of local client
cd      Change directory on the remote host
lcd     Change directory on the local client
ls      List director on the remote host
lls     List directory on the local client
mkdir   Make directory on remote host
lmkdir  Make directory on local client
get     Receive file from remote host to local client
put     Send file from local client to remote host
help    Display help text
4. Data should be saved in data/ or its subfolders 


## How to run the programs:
1. First do a test run:
mode = "1d"
do_test = True
phi = 40. # phifix mode

