# VEEAM Test Task

The current program synchronizes two folders: source and replica. The program maintain a full, identical copy of source folder at replica folder. <br>
Such synchronization is done periodically (in a period provided by the user) and in one-way: after the synchronization content of the replica folder should be modified to exactly match content of the source folder. <br><br>

> [!NOTE]
> File creation/copying/removal operations are logged to a file and to the console output. <br>

> [!WARNING]
> Folder paths, synchronization interval and log file path should be provided using the command line arguments. <br>
