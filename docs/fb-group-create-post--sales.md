# Instructions on how to create a sales post inside a facebook group using `agent-browser`  

 uv run fb_marketplace_click.py
 agent-browser --cdp 9222 snapshot
 la
 mkdir agent-browser
 cd agent-browser
 agent-browser --cdp 9222 snapshot
 agent-browser --cdp 9222 snapshot > fb-group-snapshot.txt
 vim fb-group-snapshot.txt
 agent-browser --help | grep completion
 agent-browser click e53
 agent-browser --cdp 9222 snapshot > fb-group_create-new-listing.txt
 mkdir snapshots
 mkdir snapshots/fb-groups-create-post
 mv fb-group-snapshot.txt snapshots/fb-groups-create-post/first-page.txt
 mv fb-group_create-new-listing.txt snapshots/fb-groups-create-post/2-create-new-listing-modal.txt
 mv snapshots/fb-groups-create-post/first-page.txt snapshots/fb-groups-create-post/1-first-page.txt
 la
 pwd
 la snapshots
 vim snapshots/fb-groups-create-post/2-create-new-listing-modal.txt
 agent-browser click e15
 agent-browser --cdp 9222 snapshot > snapshots/fb-groups-create-post/3-item-for-sale-modal.txt
 vim snapshots/fb-groups-create-post/3-item-for-sale-modal.txt
 agent-browser --cdp 9222 type e20 "Tst"
 agent-browser --cdp 9222 select e22 "New"
 * agent-browser --cdp 9222 snapshot > snapshots/fb-groups-create-post/3-item-for-sale-modal--2.txt
 * vim snapshots/fb-groups-create-post/3-item-for-sale-modal--2.txt
 agent-browser --cdp 9222 click e22
 * agent-browser --cdp 9222 snapshot > snapshots/fb-groups-create-post/3-item-for-sale-modal--2.txt
 * vim snapshots/fb-groups-create-post/3-item-for-sale-modal--2.txt
 agent-browser --cdp 9222 select e26 e27
 agent-browser --cdp 9222 select e22 e27
 agent-browser --cdp 9222 select e26 e27
 agent-browser --cdp 9222 click e27
 * agent-browser --cdp 9222 snapshot > snapshots/fb-groups-create-post/3-item-for-sale-modal--2.txt
 * vim snapshots/fb-groups-create-post/3-item-for-sale-modal--2.txt
 agent-browser --cdp 9222 type e24 "item description"
 agent-browser --cdp 9222 type e26 "Maribor"
 agent-browser --cdp 9222 type e26 "Maribor" --clear
 agent-browser --cdp 9222 clear e26
 agent-browser --cdp 9222 fill e26 "Maribor"
 agent-browser --cdp 9222 fill e26 "Ljubljana, Slovenia"
 agent-browser --cdp 9222 click e16
 * agent-browser --cdp 9222 snapshot > snapshots/fb-groups-create-post/3-item-for-sale-modal--3.txt
 * vim snapshots/fb-groups-create-post/3-item-for-sale-modal--3.txt
 * opencode
 agent-browser upload 'input[type="file"][accept="image/*,image/heif,image/heic"]'
 realpath ../assets/marketing_post_image.png | pbcopy
 agent-browser upload 'input[type="file"][accept="image/*,image/heif,image/heic"]' /home/bostjan/source/autocare-ai-agent/assets/marketing_post_image.png\n
 agent-browser --cdp 9222 click e34
 * agent-browser --cdp 9222 snapshot > snapshots/fb-groups-create-post/4-share-to-more-places.txt
 * vim snapshots/fb-groups-create-post/4-share-to-more-places.txt
 agent-browser --cdp 9222 click e25
 * agent-browser --cdp 9222 snapshot > snapshots/fb-groups-create-post/5-listing-published.txt
 * vim snapshots/fb-groups-create-post/4-share-to-more-places.txt
 * vim snapshots/fb-groups-create-post/5-listing-published.txt
 agent-browser --cdp 9222 get text e13
 agent-browser --cdp 9222 click e14