from rl.calc import get_distance_between_coords, get_angle_in_degrees, sign
from rl.rl_network import RLNetwork

actions = ['TurnLeft', 'TurnRight', 'Forward']
observation_keys = ['appeared', 'disappeared', 'moved_left', 'moved_right', 'state_right', 'state_left', 'centered',
                    'approached', 'receded']

SIGHT_DISTANCE = 4


class Agent:

    def __init__(self, world):
        self.world = world
        self.x_coord = 0
        self.y_coord = 0
        self.prev_x_coord = 0
        self.prev_y_coord = 0
        self.has_honey = False
        self.head_direction_x = 0
        self.head_direction_y = 0
        self.prev_head_direction_x = 0
        self.prev_head_direction_y = 0
        self.network = RLNetwork(self.world)


    def act(self):
        """
        All agent calculations and actions within 1 timestep
        :return: gained reward
        """
        action = self.network.run()
        self.update_state(action)
        observations = self.observe()

        reward = self._calculate_reward()

        self.memorize_state(action, observations, reward > 0)
        return reward


    def _calculate_reward(self):
        stumbled_on_object = [obj for obj in self.world.objects if obj.x == self.x_coord and obj.y == self.y_coord]
        back_to_hive = self.has_honey and self.world.hive_x == self.x_coord and self.world.hive_y == self.y_coord
        if stumbled_on_object and not self.has_honey:
            reward = 200
            self.has_honey = True
        elif back_to_hive:
            reward = 2000
            self.has_honey = False
        else:
            reward = -1
        return reward


    def reset(self):
        self.network = RLNetwork(self.world)
        self.head_direction_y = -1
        self.head_direction_x = 0


    def update_state(self, action):
        """
        Updates the agent's state based on the chosen action
        :param action: the action
        """
        self.prev_head_direction_x = self.head_direction_x
        self.prev_head_direction_y = self.head_direction_y
        self.prev_x_coord = self.x_coord
        self.prev_y_coord = self.y_coord

        if action == 'TurnRight':
            self.turn_right()
        elif action == 'TurnLeft':
            self.turn_left()
        elif action == 'Forward':
            self.forward()


    def turn_right(self):
        """
        Turns the agent to the right
        """
        if self.head_direction_x == 1:
            self.head_direction_x = 0
            self.head_direction_y = 1
        elif self.head_direction_y == 1:
            self.head_direction_x = -1
            self.head_direction_y = 0
        elif self.head_direction_x == -1:
            self.head_direction_x = 0
            self.head_direction_y = -1
        else:
            self.head_direction_x = 1
            self.head_direction_y = 0


    def turn_left(self):
        """
        Turns the agent to the left
        """
        if self.head_direction_x == 1:
            self.head_direction_x = 0
            self.head_direction_y = -1
        elif self.head_direction_y == 1:
            self.head_direction_x = 1
            self.head_direction_y = 0
        elif self.head_direction_x == 1:
            self.head_direction_x = 0
            self.head_direction_y = 1
        else:
            self.head_direction_x = -1
            self.head_direction_y = 0


    def forward(self):
        """
        Makes a move forward at 1 cell
        """
        self.x_coord = max(0, min(self.world.grid_size - 1, self.x_coord + self.head_direction_x))
        self.y_coord = max(0, min(self.world.grid_size - 1, self.y_coord + self.head_direction_y))
        # dx = self.prev_x_coord - self.x_coord
        # dy = self.prev_y_coord - self.y_coord


    def observe(self):
        """
        Collects observations from all object of the world
        :return:
        """
        observations = []
        for obj in self.world.objects:
            observation = self._generate_object_observation(obj)
            if observation:
                observations.append((obj, observation))
        return observations


    def memorize_state(self, action, observations, reward_received):
        """
        Stores current agent context in the neural network
        :param reward_received: True if any positive reward was received
        :param action:
        :param observations:
        :return:
        """
        self.network.memorize(action, observations, reward_received)
        self.network.learn_connectome()


    def _generate_object_observation(self, obj):
        """
        Returns a dictionary of observed features related to a particular object
        Features are optical characteristics of what happened with an object image while performing an action,
        e.g. object got closer or got away, it moved to the right or to the left etc.
        :param obj: observed object
        :return: observations dict
        """
        observation = {key: False for key in observation_keys}
        was_seen = self.object_seen(obj, self.prev_x_coord, self.prev_y_coord, self.prev_head_direction_x, self.prev_head_direction_y)
        now_seen = self.object_seen(obj, self.x_coord, self.y_coord, self.head_direction_x, self.head_direction_y)
        if was_seen and not now_seen:
            observation['disappeared'] = True
        if not was_seen and now_seen:
            observation['appeared'] = True

        if now_seen or was_seen:
            now_centered = now_seen and (self.x_coord == obj.x or self.y_coord == obj.y)
            was_centered = was_seen and (self.prev_x_coord == obj.x or self.prev_y_coord == obj.y)
            if now_centered and was_centered:
                observation['centered'] = True

            was_angle = self._get_object_angle(obj, self.prev_x_coord, self.prev_y_coord, self.prev_head_direction_x, self.prev_head_direction_y)
            now_angle = self._get_object_angle(obj, self.x_coord, self.y_coord, self.head_direction_x, self.head_direction_y)
            if was_angle < now_angle:
                observation['moved_right'] = True
            elif was_angle > now_angle:
                observation['moved_left'] = True

            was_distance = get_distance_between_coords(self.prev_x_coord, self.prev_y_coord, obj.x, obj.y)
            now_distance = get_distance_between_coords(self.x_coord, self.y_coord, obj.x, obj.y)
            if now_distance < was_distance:
                observation['approached'] = True
            if now_distance > was_distance:
                observation['receded'] = True

            if now_seen:
                observation['state_right'] = now_angle > 0
                observation['state_left'] = now_angle < 0

        return observation


    @staticmethod
    def object_seen(obj, x, y, head_x, head_y):
        """
        Calculates if the object is seen by the agent
        Implied viewing angle is 90 degrees
        """
        distance = get_distance_between_coords(x, y, obj.x, obj.y)
        if distance > SIGHT_DISTANCE:
            return False
        dx = obj.x - x
        dy = obj.y - y
        if dx == 0 and dy == 0:
            return True
        return Agent._in_quadrant(head_x, head_y, dx, dy)


    @staticmethod
    def _get_object_angle(obj, x, y, head_x, head_y):
        """
        Calculates an angle between agents' coordinates and the object depending on the agent's sight direction
        :param obj: object
        :param x: agent's X coord
        :param y: agent's Y coord
        :param head_x: head direction X coord
        :param head_y: head direction Y coord
        :return:
        """
        dx = obj.x - x
        dy = obj.y - y
        if dx == 0 and dy == 0:
            return 0
        angle = 0
        if head_x == 1:
            angle = Agent._get_object_angle_on_direction(dy, dx, flip_sign=False, subtract_from_180=False)
            # dy_sign = sign(dy)
            # dy = abs(dy)
            # if dx > 0:
            #     angle = dy_sign * get_angle_in_degrees(dy / dx)
            # elif dx < 0:
            #     angle = dy_sign * (180 - get_angle_in_degrees(dy / -dx))
            # else:
            #     angle = dy_sign * 90

        if head_x == -1:
            angle = Agent._get_object_angle_on_direction(dy, dx, flip_sign=True, subtract_from_180=True)
            # dy_sign = -sign(dy)
            # dy = abs(dy)
            # if dx > 0:
            #     angle = dy_sign * (180 - get_angle_in_degrees(dy / dx))
            # elif dx < 0:
            #     angle = dy_sign * get_angle_in_degrees(dy / -dx)
            # else:
            #     angle = dy_sign * 90

        if head_y == -1:
            angle = Agent._get_object_angle_on_direction(dx, dy, flip_sign=False, subtract_from_180=True)
            # dx_sign = sign(dx)
            # dx = abs(dx)
            # if dy < 0:
            #     angle = dx_sign * get_angle_in_degrees(dx / -dy)
            # elif dy > 0:
            #     angle = dx_sign * (180 - get_angle_in_degrees(dx / dy))
            # else:
            #     angle = dx_sign * 90

        if head_y == 1:
            angle = Agent._get_object_angle_on_direction(dx, dy, flip_sign=True, subtract_from_180=False)
            # dx_sign = -sign(dx)
            # dx = abs(dx)
            # if dy < 0:
            #     angle = dx_sign * (180 - get_angle_in_degrees(dx / -dy))
            # elif dy > 0:
            #     angle = dx_sign * get_angle_in_degrees(dx / dy)
            # else:
            #     angle = dx_sign * 90

        return angle


    @staticmethod
    def _get_object_angle_on_direction(dividend, denominator, flip_sign, subtract_from_180):
        """
        Calculates an angle based on coordinates deltas
        :param dividend:
        :param denominator:
        :param flip_sign:
        :param subtract_from_180:
        :return:
        """
        div_sign = -sign(dividend) if flip_sign else sign(dividend)
        angle_sign = -sign(denominator) if subtract_from_180 else sign(denominator)
        subtraction_base = 180 if subtract_from_180 else 0
        dividend = abs(dividend)
        if denominator > 0:
            angle = div_sign * (subtraction_base + angle_sign * get_angle_in_degrees(dividend / denominator))
        elif denominator < 0:
            angle = div_sign * ((180 - subtraction_base) + angle_sign * get_angle_in_degrees(dividend / -denominator))
        else:
            angle = div_sign * 90
        return angle


    @staticmethod
    def _in_quadrant(head_x, head_y, dx, dy):
        if head_x == 1:
            return dx > 0 and abs(dy) <= dx
        if head_x == -1:
            return dx < 0 and abs(dy) <= -dx
        if head_y == -1:
            return dy < 0 and -dy >= abs(dx)
        if head_y == 1:
            return dy > 0 and dy >= abs(dx)