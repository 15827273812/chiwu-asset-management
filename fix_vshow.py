#!/usr/bin/env python3
"""Test: re-serve frontend.html with v-show replaced by v-if"""
import re

with open('/home/mzh205/.openclaw/workspace/chiwu/frontend.html', 'r') as f:
    content = f.read()

# Replace v-show with v-if
content = content.replace('v-show="activeTab', 'v-if="activeTab')
content = content.replace('v-show="showStatsSettingsSection"', 'v-if="showStatsSettingsSection"')
content = content.replace('v-show="showCatsSection"', 'v-if="showCatsSection"')
content = content.replace('v-show="showChannelsSection"', 'v-if="showChannelsSection"')

with open('/home/mzh205/.openclaw/workspace/chiwu/frontend_vif.html', 'w') as f:
    f.write(content)

print('Created frontend_vif.html with v-show→v-if')
