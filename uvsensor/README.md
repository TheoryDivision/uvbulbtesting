## UVBot Commands

- The experiment and Slack interaction (messages and file uploads) run in one thread to prevent memory problems. 
- Once a graphing task has been scheduled, and you change the graphing interval parameter, you have to wait for the scheduled task to complete before seeing the change in the graphing interval.
    - This happens with all scheduled tasks but it's more obvious with graphing becuase intervals tend to be bigger.
- Requesting a graph does not force the grapher to make a new one. It uploads the latest graph created during a scheduled task.
    - This is becuase graphing blocks the thread while it completes. If there are an excessive number of graph requests, and lots of data to process, regularly scheduled tasks may be disrupted. 

&nbsp;

| Command | Result |
| ------ | ------ |
| hello/hai/sup/hi/hey | Greets |
| data/csv | Uploads latest data |
| plot/graph | Uploads latest graph |
| loop/cycles | Prints current cycle number |
| thead | Replies in the graphing thread and broadcasts to channel |
| param | Prints all experiment parameters |
| latest | Prints latest set of data from sensors |
| adjust power on {time} | Changes on interval |
| adjust power off {time} | Changes off interval |
| adjust rw on {time} | Changes read/write interval in the on state |
| adjust rw off {time} | Changes read/write interval in the off state |
| adjust graph int {time} | Changes graphing interval |
| adjust graph line {time} | Changes number of lines of data used to generate graph |

{time} = [floating number] sec, min, hour (plural also works)*\
*Only one unit of time per command
