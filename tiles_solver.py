"""
File: tiles_solver.py
Author: Jeremy Ephron
---------------------
Plays the NYTimes online game tiles using Selenium webdriver.

"""

import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


class Tile():
    def __init__(self, tile_webelement):
        self.tile_webelement = tile_webelement
        self.layers = [
            tile_webelement.find_element_by_css_selector(
                f'.tls-tile__frame > svg:nth-child({i})'
            ).find_element_by_css_selector('use').get_attribute('xlink:href')
            for i in range(2, 5)
        ]
    
    def isMatch(self, other):
        for i in range(len(self.layers)):
            if self.layers[i] is None or other.layers[i] is None:
                continue

            if self.layers[i] == other.layers[i]:
                return True

        return False

    def isEmpty(self):
        return all([x is None for x in self.layers])

    def eliminate(self, other):
        for i in range(len(self.layers)):
            if self.layers[i] is None or other.layers[i] is None:
                continue

            if self.layers[i] == other.layers[i]:
                self.layers[i] = None
                other.layers[i] = None

    def click(self, prev=None):
        self.tile_webelement.click()

        if prev is not None:
            self.eliminate(prev)


def setup_webdriver(*args):
    options = webdriver.ChromeOptions()
    for arg in args:
        options.add_argument(arg)

    driver = webdriver.Chrome(options=options)

    # I recommend always setting an implicit wait unless you have good reason  not to do so, network connections are
    # a slow and tricky thing.
    driver.implicitly_wait(10)  # if it can't find the element, the driver will wait for 10s before throwing an error.
    return driver


def learn_tile_grid(driver):
    tiles = driver.find_elements_by_css_selector('#tls-tileset > div.tls-tile')
    return [Tile(tile) for tile in tiles]


def play_tiles(driver, tile_grid):
    prev = tile_grid[0]
    tile_grid[0].click()

    while len(tile_grid) > 0:
        if prev is None:
            prev = tile_grid[0]
            tile_grid[0].click()

        for i in range(len(tile_grid)):
            curr = tile_grid[i]

            if prev is curr:
                continue

            if prev.isMatch(curr):
                curr.click(prev=prev)

                if prev.isEmpty():
                    tile_grid.remove(prev)

                if curr.isEmpty():
                    tile_grid.remove(curr)
                    prev = None

                else:
                    prev = curr

                break



if __name__ == '__main__':
    driver = setup_webdriver()

    # Go to puzzle site
    driver.get('https://www.nytimes.com/puzzles/tiles')

    # Click play
    play_btn = driver.find_element_by_xpath('//*[@id="pzm-welcome"]/div/div[3]/button[1]')
    screen = driver.find_element_by_xpath('//*[@id="portal-game-modals"]/div')
    actions = ActionChains(driver)
    actions.move_to_element(screen).click(play_btn).perform()

    tile_grid = learn_tile_grid(driver)
    play_tiles(driver, tile_grid)

    time.sleep(5)
    driver.quit()

