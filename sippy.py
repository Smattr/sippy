#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, re, subprocess, sys

try:
    import pygame
except ImportError:
    print >>sys.stderr, 'Failed to import pygame. Is it installed?'
    sys.exit(-1)

BG_COLOR = (0, 0, 0) # Black
FONT_SIZE = 36
HEADING_SIZE = 48
HEADING_COLOR = (180, 180, 180) # Lighter grey
UNSELECTED_COLOR = (70, 70, 70) # Grey
SELECTED_COLOR = (255, 255, 255) # White
EXTENSIONS_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'extensions')

mode = None # Calculated on startup.

def fill(xs, d):
    '''Do string substitution on an array of target strings.'''
    return map(lambda x: x % d, xs)

class Handler(object):
    def __init__(self, matches, command):
        self.matches = matches
        self.command = command

    def open(self, item):
        # Go out of full screen so the media player can take over.
        pygame.display.set_mode(mode)

        # Open the file.
        ret = subprocess.call(fill(self.command, {'file':item}))

        # Switch back to full screen.
        pygame.display.set_mode(mode, pygame.FULLSCREEN)
        return ret

HANDLERS = [
    Handler(r'\.sh$', ['bash', '%(file)s']),
    Handler(r'\.py$', ['python', '%(file)s']),
    Handler(r'\.(bin|cue)$', [os.path.join(EXTENSIONS_PATH, 'binplayer.sh'), '%(file)s', '-fs']),
    Handler(r'.*', ['mplayer', '-fs', '%(file)s']), # Catch all
]

font = None
heading_font = None
def display(screen, heading, items, selected):
    global font, heading_font

    # Wipe existing artifacts.
    screen.fill(BG_COLOR)

    # Cache these font objects to avoid reconstructing them each refresh.
    if not font:
        font = pygame.font.Font(None, FONT_SIZE)
    if not heading_font:
        heading_font = pygame.font.Font(None, HEADING_SIZE)

    # Render the heading
    text = heading_font.render(heading, 1, HEADING_COLOR)
    screen.blit(text, (10, 10))

    height = screen.get_height()
    width = screen.get_width()

    if 20 + HEADING_SIZE + FONT_SIZE * len(items) > height:
        # Items won't fit on screen. We'll need to simulate scrolling.
        # Calculate the window of items we'll show.
        max_items = (height - 20 - HEADING_SIZE) / FONT_SIZE
        offset = selected - (max_items / 2)
        if offset + max_items > len(items) - 1:
            offset = len(items) - max_items
        if offset < 0:
            offset = 0
        segment = items[offset:offset + max_items]

        # Show arrows if there are items off screen.
        if offset > 0:
            # There are more items off screen above.
            text = font.render(u'↑', 1, UNSELECTED_COLOR)
            screen.blit(text, (width - 30, 20 + HEADING_SIZE))
        if offset + max_items < len(items):
            # There are more items off screen below.
            text = font.render(u'↓', 1, UNSELECTED_COLOR)
            screen.blit(text, (width - 30, 20 + HEADING_SIZE + FONT_SIZE * (max_items - 1)))
    else:
        # Everything fits on screen :)
        segment = items
        offset = 0

    # Render the items.
    for i, item in enumerate(segment):
        if i + offset == selected:
            color = SELECTED_COLOR
        else:
            color = UNSELECTED_COLOR
        text = font.render(item, 1, color)
        screen.blit(text, (20, 20 + HEADING_SIZE + FONT_SIZE * i))

    # Pull the trigger.
    pygame.display.flip()

def get_items(root, current):
    try:
        items = sorted(os.listdir(current))
    except:
        items = []
    if current != root:
        # If we're not at the root, give the user a way up.
        items = ['..'] + items
    return items

def main():
    global mode

    if len(sys.argv) != 2:
        print >>sys.stderr, 'Usage: %s source' % sys.argv[0]
        return -1

    current = root = os.path.abspath(sys.argv[1])
    selected = 0
    items = get_items(root, current)

    # Setup our background.
    pygame.init()
    pygame.display.set_caption('sippy')
    desktop_width = pygame.display.Info().current_w
    desktop_height = pygame.display.Info().current_h
    mode = (desktop_width, desktop_height)
    screen = pygame.display.set_mode(mode, pygame.FULLSCREEN)
    pygame.mouse.set_visible(False)
    pygame.event.set_allowed(None)
    pygame.event.set_allowed(pygame.KEYDOWN)

    def refresh():
        '''Redraw the screen.'''
        assert current.startswith(root)
        path = current[len(root):]
        if current == root:
            path = '/'
        display(screen, path, items, selected)
    refresh()

    while True:
        ev = pygame.event.wait()

        if ev.key in [pygame.K_ESCAPE, pygame.K_LEFT]:
            # Go up a directory or, if we're at root, exit.
            if current == root:
                return 0
            else:
                current = os.path.abspath(os.path.join(current, '..'))
                items = get_items(root, current)
                selected = 0
                refresh()

        # Item selection.
        elif ev.key == pygame.K_UP:
            if selected != 0:
                selected -= 1
                refresh()
        elif ev.key == pygame.K_DOWN:
            if selected != len(items) - 1:
                selected += 1
                refresh()

        elif ev.key in [pygame.K_RETURN, pygame.K_RIGHT]:
            # Enter selection. Either go into the selected directory or play
            # the selected file.
            path = os.path.join(current, items[selected])
            if os.path.isdir(path):
                current = os.path.abspath(os.path.join(current, items[selected]))
                items = get_items(root, current)
                selected = 0
                refresh()
            else:
                for h in HANDLERS:
                    if re.search(h.matches, path, re.IGNORECASE):
                        h.open(path)
                        break
                # The mode toggling `open` has done will have blanked the
                # screen, so refresh it.
                refresh()

if __name__ == '__main__':
    sys.exit(main())
