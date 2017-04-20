import os

nprocs = 10 
os.chdir("jobs")

nblocks = 10 
for rank in xrange(nprocs):
    with open("hkljob_%03d.sbatch"%rank, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write("\n")
        f.write("#SBATCH --job-name=hkl_%03d\n"%rank)
        f.write("#SBATCH --output=hkljob_%03d.out\n"%rank)
        f.write("#SBATCH --error=hkljob_%03d.err\n"%rank)
        f.write("#SBATCH --time=0:10:00\n")
        f.write("#SBATCH --qos=normal\n")
        f.write("#SBATCH --partition=iric\n")
        f.write("#SBATCH --nodes=1\n")
        f.write("#SBATCH --ntasks-per-node=1\n")
        if rank == nprocs-1:
            f.write("#SBATCH --mail-type=END\n")
            f.write("#SBATCH --mail-user=phsun@stanford.edu\n")
        f.write("\n")

        f.write("cd ../\n\n")
        i_block = rank
        while i_block < nblocks:
            f.write("python hklhist_calscans.py %d\n"%(i_block))
            i_block += nprocs

    os.system("sbatch hkljob_%03d.sbatch" % rank)
