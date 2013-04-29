"""An url dispatcher for the plugin."""

from addon import connect_resources
connect_resources()

from addon import current_url
import subreddit_details
import subreddit_list
import youtube

if current_url.match(r'^$'):
    subreddit_list.show()

elif current_url.match(r'^add_subreddit/$'):
    subreddit_list.add_subreddit()

elif current_url.match(r'^remove_subreddit/$'):
    subreddit_list.remove_subreddit()

elif current_url.match(r'^remove_subreddit/(\w+)/$'):
    subreddit_name = current_url.group(1)
    subreddit_list.remove_subreddit(subreddit_name)

elif current_url.match(r'^media/youtube/([-_\w]+)/$'):
    video_id = current_url.group(1)
    youtube.show(video_id)

elif current_url.match(r'^r/(\w+)/$'):
    subreddit_name = current_url.group(1)
    subreddit_details.show(subreddit_name)

else:
    assert False, 'Unexpected URL: ' + str(current_url)
