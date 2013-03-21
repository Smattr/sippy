#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, subprocess, sys

try:
    import pygame
except ImportError:
    print >>sys.stderr, 'Failed to import pygame. Is it installed?'
    sys.exit(-1)

BG_COLOR = (0, 0, 0) # Black
FONT_SIZE = 36
HEADING_SIZE = 48
HEADING_COLOR = (180, 180, 180) # Lighter grey
UNSELECTED_COLOR = (150, 150, 150) # Grey
SELECTED_COLOR = (255, 255, 255) # White
GUTTER_HEIGHT = 50 # Space to reserve at bottom (to account for window manager
                   # stuffs)
MEDIA_PLAYER = ['mplayer', '-fs', '%(file)s']

mode = None # Calculated on startup.

def fill(xs, d):
    '''Do string substitution on an array of target strings.'''
    return map(lambda x: x % d, xs)

def play(filename):
    # Go out of full screen so the media player can take over.
    pygame.display.set_mode(mode)

    # Play the file.
    ret = subprocess.call(fill(MEDIA_PLAYER, {
        'file':filename,
    }))

    # Switch back to full screen.
    pygame.display.set_mode(mode, pygame.FULLSCREEN)
    return ret

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

    if 20 + HEADING_SIZE + FONT_SIZE * len(items) + GUTTER_HEIGHT > height:
        # Items won't fit on screen. We'll need to simulate scrolling.
        # Calculate the window of items we'll show.
        max_items = (height - 20 - HEADING_SIZE - GUTTER_HEIGHT) / FONT_SIZE
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
        # FIXME: Yuck. Handle this better.
        items = ['<FAILED>']
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

    def refresh():
        '''Redraw the screen.'''
        assert current.startswith(root)
        path = current[len(root):]
        if current == root:
            path = '/%s' % path
        display(screen, path, items, selected)
    refresh()

    while True:
        ev = pygame.event.wait()

        # Skip things like mouse events.
        if ev.type != pygame.KEYDOWN:
            continue

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
                play(path)
                # The mode toggling `play` has done will have blanked the
                # screen, so refresh it.
                refresh()

if __name__ == '__main__':
    sys.exit(main())
