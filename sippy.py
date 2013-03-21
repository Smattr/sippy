#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, subprocess, sys

try:
    import pygame
except ImportError:
    print >>sys.stderr, 'Failed to import pygame. Is it installed?'
    sys.exit(-1)

DEBUG = False
BG_COLOR = (0, 0, 0) # Black
FONT_SIZE = 36
HEADING_SIZE = 48
HEADING_COLOR = (180, 180, 180) # Lighter grey
UNSELECTED_COLOR = (150, 150, 150) # Grey
SELECTED_COLOR = (255, 255, 255) # White
MEDIA_PLAYER = ['mplayer', '-fs', '%(file)s']

def fill(xs, d):
    assert isinstance(xs, list)
    assert isinstance(d, dict)
    return map(lambda x: x % d, xs)

def play(filename):
    return subprocess.call(fill(MEDIA_PLAYER, {
        'file':filename,
    }))

font = None
heading_font = None
def display(screen, heading, items, selected):
    global font, heading_font
    screen.fill(BG_COLOR)
    if not font:
        font = pygame.font.Font(None, FONT_SIZE)
    if not heading_font:
        heading_font = pygame.font.Font(None, HEADING_SIZE)
    text = heading_font.render(heading, 1, HEADING_COLOR)
    screen.blit(text, (10, 10))
    height = screen.get_height()
    width = screen.get_width()
    if 20 + HEADING_SIZE + FONT_SIZE * len(items) > height:
        # Items won't fit on screen. We'll need to show scrolling.
        max_items = (height - 20 - HEADING_SIZE) / FONT_SIZE
        offset = selected - (max_items / 2)
        if offset + max_items > len(items) - 1: offset = len(items) - max_items
        if offset < 0: offset = 0
        segment = items[offset:offset + max_items]
        if offset > 0:
            text = font.render(u'↑', 1, UNSELECTED_COLOR)
            screen.blit(text, (width - 30, 20 + HEADING_SIZE))
        if offset + max_items < len(items):
            text = font.render(u'↓', 1, UNSELECTED_COLOR)
            screen.blit(text, (width - 30, 20 + HEADING_SIZE + FONT_SIZE * (max_items - 1)))
    else:
        segment = items
        offset = 0
    for i, item in enumerate(segment):
        if i + offset == selected:
            color = SELECTED_COLOR
        else:
            color = UNSELECTED_COLOR
        text = font.render(item, 1, color)
        screen.blit(text, (20, 20 + HEADING_SIZE + FONT_SIZE * i))
    pygame.display.flip()

def get_items(root, current):
    try:
        items = sorted(os.listdir(current))
    except:
        items = ['<FAILED>']
    if current != root:
        items = ['..'] + items
    return items

def main():
    if len(sys.argv) != 2:
        print >>sys.stderr, 'Usage: %s source' % sys.argv[0]
        return -1

    current = root = os.path.abspath(sys.argv[1])
    selected = 0
    items = get_items(root, current)
    try:
        items = os.listdir(root)
    except:
        print >>sys.stderr, 'Failed to open %s' % root
        return -1

    pygame.init()
    pygame.display.set_caption('sippy')
    if DEBUG:
        screen = pygame.display.set_mode(640, 480)
    else:
        screen = pygame.display.set_mode(pygame.display.list_modes()[0])
        pygame.mouse.set_visible(False)

    def refresh():
        assert current.startswith(root)
        path = current[len(root):]
        if current == root:
            path = '/%s' % path
        display(screen, path, items, selected)
    refresh()

    def transition(cd):
        current = os.path.abspath(os.path.join(current, items[selected]))
        items = get_items(root, current)
        selected = 0
        refresh()

    while True:
        ev = pygame.event.wait()
        if ev.type != pygame.KEYDOWN:
            continue
        if ev.key in [pygame.K_ESCAPE, pygame.K_LEFT]:
            if current == root:
                return 0
            else:
                current = os.path.abspath(os.path.join(current, '..'))
                items = get_items(root, current)
                selected = 0
                refresh()
        elif ev.key == pygame.K_UP:
            if selected != 0:
                selected -= 1
                refresh()
        elif ev.key == pygame.K_DOWN:
            if selected != len(items) - 1:
                selected += 1
                refresh()
        elif ev.key in [pygame.K_RETURN, pygame.K_RIGHT]:
            path = os.path.join(current, items[selected])
            if os.path.isdir(path):
                current = os.path.abspath(os.path.join(current, items[selected]))
                items = get_items(root, current)
                selected = 0
                refresh()
            else:
                play(path)

if __name__ == '__main__':
    sys.exit(main())
