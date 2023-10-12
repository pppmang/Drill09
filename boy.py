import math

from pico2d import load_image, get_time
from sdl2 import SDL_KEYDOWN, SDLK_SPACE, SDLK_RIGHT, SDL_KEYUP, SDLK_LEFT


def space_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE


def right_down(e):  # 오른쪽 방향키를 누르고 있는 상태에 대한 함수 (idle -> run)
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT


def right_up(e):  # 오른쪽 방향키에서 손을 뗀 상태에 대한 함수 (run -> idle)
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT


def left_down(e):  # 왼쪽 방향키를 누르고 있는 상태에 대한 함수 (idle -> run)
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT


def left_up(e):  # 왼쪽 방향키에서 손을 뗀 상태에 대한 함수 (run -> idle)
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT


def time_out(e):
    return e[0] == 'TIME_OUT'


class Sleep:  # 특정함수를 모아 그루핑하는 역할을 하는 클래스
    @staticmethod
    def enter(boy, e):
        boy.frame = 0
        print('고개 숙이기')

    @staticmethod
    def exit(boy, e):
        print('고개 들기')

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        print('드르렁')

    @staticmethod
    def draw(boy):
        if boy.action == 2:
            boy.image.clip_composite_draw(boy.frame * 100, 200, 100, 100, math.pi / 2, '', boy.x - 25,
                                          boy.y - 25, 100, 100)
        else:
            boy.image.clip_composite_draw(boy.frame * 100, 300, 100, 100, math.pi / 2, '', boy.x - 25,
                                          boy.y - 25, 100, 100)
        pass


class Run:  # 특정함수를 모아 그루핑하는 역할을 하는 클래스
    @staticmethod
    def enter(boy, e):  # 왜 run 으로 왔는지에 대한 정보가 있어야 하기 때문에 event 를 전달해야 함.
        if right_down(e) or left_up(e):  # 오른쪽으로 RUN
            boy.dir, boy.action = 1, 1
        elif left_down(e) or right_up(e):  # 왼쪽으로 RUN
            boy.dir, boy.action = -1, 0

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        boy.x += boy.dir * 5
        pass

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)
        pass


class AutoRun:
    @staticmethod
    def enter(boy, e):
        boy.frame = 0
        boy.dir = 1
        if boy.dir == 1:
            boy.action = 1
        elif boy.dir == -1:
            boy.action = 0


    @staticmethod
    def exit(boy, e):
        boy.action = 3
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        boy.x += boy.dir * 10
        pass

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y, 200, 200)
        pass


class Idle:  # 특정함수를 모아 그루핑하는 역할을 하는 클래스
    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        if get_time() - boy.start_time > 3.0:
            boy.state_machine.handle_event(('TIME_OUT', 0))

    @staticmethod
    def enter(boy, e):
        if boy.action == 0:
            boy.action = 2
        elif boy.action == 1:
            boy.action = 3
        boy.dir = 0
        boy.frame = 0
        boy.start_time = get_time()

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)
        pass


class StateMachine:
    def __init__(self, boy):
        self.boy = boy  # StateMachine 은 boy 를 자신에게 저장함.
        self.cur_state = Idle
        self.table = {
            Sleep: {right_down: Run, left_down: Run, right_up: Run, left_up: Run, space_down: Idle},
            # dictionary of dictionary 로 표현
            Idle: {right_down: Run, left_down: Run, left_up: Run, right_up: Run, time_out: Sleep},
            Run: {right_down: Idle, left_down: Idle, right_up: Idle, left_up: Idle}
        }

    def start(self):
        self.cur_state.enter(self.boy, ('START', 0))

    def update(self):
        self.cur_state.do(self.boy)

    def handle_event(self, e):  # state event handling
        for check_event, next_state in self.table[self.cur_state].items():
            # dictionary 안에 있는 item 확인 후, 이벤트가 발생하면 다음 상태로 변함.
            if check_event(e):
                self.cur_state.exit(self.boy, e)  # 다음 상태로 넘어가기 전 상태의 exit action
                self.cur_state = next_state  # exit action 후에 다음 상태를 현재 상태로 바꿈.
                self.cur_state.enter(self.boy, e)  # 현재 상태의 entry action
                return True  # 성공적으로 이벤트 변환
        return False  # 이벤트를 소모하지 못함.
        pass

    def draw(self):
        self.cur_state.draw(self.boy)


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.dir = 0
        self.action = 3
        self.image = load_image('animation_sheet.png')
        self.state_machine = StateMachine(self)  # 소년 객체에 대한 정보는 self 에 들어있기 때문에 self 를 전달함.
        self.state_machine.start()

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        self.state_machine.handle_event(('INPUT', event))
        pass

    def draw(self):
        self.state_machine.draw()
