#Install Redis

Install the files following these instructions http://redis.io/download

Install into /usr/local/redis

Install the config files into:

<pre>
/usr/local/etc/redis-ditchmgr.conf
</pre>

# Launch Redis Manually

<pre>
sudo redis-server /usr/local/etc/redis-ditchmgr.conf
</pre>

#Setup Redis for auto-launch

With auto-launch setup, redis will start when the system reboots

Copy the org.redis.redis-ditchmgr.plist files to /Library/LaunchDaemons

<pre>
sudo cp org.redis.redis-ditchmgr.plist /Library/LaunchDaemons
</pre>

Load the launchctrl files:

<pre>
sudo launchctl load /Library/LaunchDaemons/org.redis.redis-ditchmgr.plist
</pre>

Start the launchctrl files:

<pre>
sudo launchctl start org.redis.redis-ditchmgr
</pre>

# Setting up a develoment DB

Copy the files in edsdb to the dir location specfied inthe redis.conf 
