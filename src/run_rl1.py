import random

from rl.rl_app import RLApp
from rl.world import World
from rl.world_object import WorldObject


def main():
    random.seed(45)
    world = World()
    obj = WorldObject('honey source', world, 3, 0)
    world.objects.append(obj)
    app = RLApp(world)
    app.run()


if __name__ == '__main__':
    main()