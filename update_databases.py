#!/usr/bin/python

import sys
import os
import shutil

def print_help():
    print "Usage: update_databases.py [-d databases] [-b wwwblast_location] [-c cpus]"
    print "       where"
    print "         -d databases is the directory containing the BLAST databases. Default is ./db"
    print "         -b wwwblast_location is the directory containing the wwwBLAST files. Default is . (current dir)"
    print "         -c cpus the number of CPUs to use for BLAST. Default is 4"
    print " "
    exit()

def parse_params(params, args):
    for i in args:
        if args[i] == "-d":
            try:
                params["databases"] = args[i+1]
            except:
                pass
        if args[i] == "-b":
            try:
                params["wwwblast_location"] = args[i+1]
            except:
                pass
        if args[i] == "-c":
            try:
                params["cpus"] = args[i+1]
            except:
                pass

def read_params(params):
    if params["databases"] == "":
        try:
            print "Please type the location for the BLAST databases [./db]:"
            params["databases"]=raw_input('')
            if params["databases"] ==  "":
                params["databases"]="./db"
        except ValueError:
            pass
    if params["wwwblast_location"] == "":
        try:
            print "Please type the location for the wwwBLAST sources [.]:"
            params["wwwblast_location"]=raw_input('').rstrip("/")
            if params["wwwblast_location"] ==  "":
                params["wwwblast_location"]="."
        except ValueError:
            pass
    if params["cpus"] == "":
        try:
            print "Please type the number of CPUs to use for BLAST [4]:"
            params["cpus"]=raw_input('')
            if params["cpus"] ==  "":
                params["cpus"]="4"
        except ValueError:
            pass

def check_params(params):
    if params["databases"] == "" or not(os.path.isdir(params["databases"])):
        print "Databases dir is not valid."
        print_help()
    if params["wwwblast_location"] == "" or not(os.path.isdir(params["wwwblast_location"])):
        print "wwwBLAST dir is not valid."
        print_help()
    if not(is_number(params["cpus"])):
        print str(params["cpus"]) + " is not a valid CPU number."
        print_help()

def is_number(n):
    try:
        int(n)
        return True
    except ValueError:
        return False

def read_databases(params):
    params["protein_dbs"]=[]
    params["nucleotides_dbs"]=[]
    params["cdd_dbs"]=[]
    for filename in os.listdir(params["databases"]):
        filename, file_extension = os.path.splitext(filename)
        if file_extension == ".psq":
            params["protein_dbs"].append(filename)
        elif file_extension == ".nsq":
            params["nucleotides_dbs"].append(filename)
    for filename in os.listdir(params["databases"] + "/CDD/"):
        filename, file_extension = os.path.splitext(filename)
        if file_extension == ".psq":
            params["cdd_dbs"].append("CDD/" + filename)

def update_files(params):
    content = ""
    content = content + "NumCpuToUse    " + str(params["cpus"]) + "\n"
    content = content + "" + "\n"
    content = content + "blastn " + " ".join(params["nucleotides_dbs"]) + "\n"
    content = content + "blastp " + " ".join(params["protein_dbs"]) + "\n"
    content = content + "blastx " + " ".join(params["protein_dbs"]) + "\n"
    content = content + "tblastn " + " ".join(params["nucleotides_dbs"]) + "\n"
    content = content + "tblastx " + " ".join(params["nucleotides_dbs"]) + "\n"
    create_new_file(params["wwwblast_location"], "blast.rc", content)
    create_new_file(params["wwwblast_location"], "psiblast.rc", content)

    content = ""
    content = content + "NumCpuToUse    " + str(params["cpus"]) + "\n"
    content = content + "" + "\n"
    content = content + "blastp " + " ".join(params["cdd_dbs"]) + "\n"
    content = content + "blastx " + " ".join(params["cdd_dbs"]) + "\n"
    create_new_file(params["wwwblast_location"], "rpsblast.rc", content)

    content = ""
    for db in params["nucleotides_dbs"]:
        content = content + "<option>" + db + "</option>" + "\n"
    for db in params["protein_dbs"]:
        content = content + "<option>" + db + "</option>" + "\n"
    complete_template(params["wwwblast_location"], "blast_cs.html", content)
    complete_template(params["wwwblast_location"], "psiblast_cs.html", content)

    content = ""
    for db in params["cdd_dbs"]:
        content = content + "<option value='" + db + "'>" + db.replace("CDD/", "") + "</option>" + "\n"
    complete_template(params["wwwblast_location"], "rpsblast_cs.html", content)

def create_new_file(directory, filename, content):
    shutil.copyfile(directory + "/" + filename, directory + "/old_files/" + filename)
    file = open(directory + "/" + filename,"w")
    file.write(content)
    file.close()

def complete_template(directory, filename, content):
    # Read in the file
    with open(directory + "/templates/" + filename, 'r') as file :
        filedata = file.read()
        file.close()
        # Replace the target string
        filedata = filedata.replace('$${DATABASES}', content)
        # Write the file out again
        shutil.copyfile(directory + "/" + filename, directory + "/old_files/" + filename)
        with open(directory + "/" + filename, 'w') as file:
          file.write(filedata)
        file.close()

# Get the total number of args passed to the demo.py
total = len(sys.argv)

params={
    "databases" : "",
    "wwwblast_location" : "",
    "cpus" : ""
}

if(total == 1):
    #ask
    read_params(params)
    check_params(params)
elif(total == 3 or total == 5 or total == 7):
    parse_params(params, sys.argv)
    read_params(params)
    check_params(params)
else:
    print_help()

read_databases(params)
update_files(params)
exit(0)
