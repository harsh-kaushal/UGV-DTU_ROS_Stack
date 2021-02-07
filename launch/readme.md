# Launching Sequence

- First Launch the world by
  ```sh
  roslaunch ugv_bot ugvbot_world.launch
  ```
 - Next launch the gmapping module
   ```sh 
   roslaunch ugv_bot ugvbot_gmapping.launch 
   ```
 - Finally launch the movebase / costmap2d module
   ```sh
   roslaunch ugv_bot ugvbot_movebase.launch 
   ```
Movebase launch file will also launch rviz with final.rivz configuration file, \
which should look something like this,

  ![](Images_launch/final_config.png)

 
