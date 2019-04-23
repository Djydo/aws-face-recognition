import subprocess
"""
Program copies all file contents from all sub-directories into a new directory    
    root_directory  
         |
         |--subdirectory1
         |
         |--subdirectory2
         |
         |--     :
         |
         |--subdirectoryN
         |
         |_ new_directory (contents of subdirectory1 to subdirectoryN)
         
The program is used to process content from the following links
   Image source: http://vis-www.cs.umass.edu/lfw/ 
   Download link: http://vis-www.cs.umass.edu/lfw/lfw.tgz
"""


def get_files(path_to_dir):
    root_dir = subprocess.check_output(['ls', path_to_dir]).decode('utf-8')
    sub_dir = root_dir[:-1].split('\n')
    return sub_dir


if __name__ == "__main__":
    path = '/home/<username>/Downloads/lfw/'
    home_directory = get_files(path)
    subprocess.check_output(['mkdir', path + '_all_files'])
    print('copying file ...')
    for item in home_directory:
        content = get_files(path + str(item))
        for it in content:
            subprocess.check_output(['cp', path + item + '/' + it, path + '_all_files'])
    print('Done!')
