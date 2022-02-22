from pypga.modules.counter import Counter
from pypga.core import TopModule
import pytest
import time
import math


class MyExampleCounter(TopModule):
    default_counter: Counter()

    _custom_up_counter_kwargs = {
        "width": 27,
        "default_start": 5,
        "default_step": 4,
        "default_stop": 2**27 - 3,
        "default_on": False,
    }
    custom_up_counter: Counter(**_custom_up_counter_kwargs, direction="up")

    _custom_down_counter_kwargs = {
        "width": 27,
        "default_start": 2**27 - 2,
        "default_step": 2,
        "default_stop": 100,
        "default_on": False,
    }
    custom_down_counter: Counter(**_custom_down_counter_kwargs, direction="down")


@pytest.fixture(scope="module")
def my_example_counter(host, board):
    dut = MyExampleCounter.run(host=host, board=board)
    yield dut
    dut.stop()


class TestCounter:
    @pytest.fixture
    def counter(self, my_example_counter):
        counter = my_example_counter.default_counter
        counter.reset()
        yield counter

    @pytest.mark.parametrize("delay", [0.1, 0.3])
    def test_count_rate(self, counter, delay):
        assert not counter.done
        count0 = counter.count
        start_time = time.time()
        time.sleep(delay)
        count1 = counter.count
        end_time = time.time()
        if count1 < count0:
            count1 += 2**32
        rate = (count1 - count0) / (end_time - start_time)
        assert math.isclose(rate, 125e6, rel_tol=0.1)


class TestCustomUpCounter:
    direction = "up"

    @pytest.fixture
    def _counter(self, my_example_counter):
        return my_example_counter.custom_up_counter

    @pytest.fixture
    def counter_defaults(self, my_example_counter):
        return my_example_counter._custom_up_counter_kwargs

    @pytest.fixture
    def counter(self, _counter, counter_defaults):
        _counter.on = counter_defaults["default_on"]
        _counter.start = counter_defaults["default_start"]
        _counter.step = counter_defaults["default_step"]
        _counter.stop = counter_defaults["default_stop"]
        _counter.reset()
        yield _counter

    def test_initial_state(self, counter, counter_defaults):
        assert not counter.on
        assert counter.start == counter_defaults["default_start"]
        assert counter.step == counter_defaults["default_step"]
        assert counter.stop == counter_defaults["default_stop"]

    def test_stop(self, counter, counter_defaults):
        assert not counter.done
        assert counter.count == counter.start
        counts = abs(counter.stop - counter.start)
        steps = counts / counter.step
        delay = steps / 125e6
        counter.on = True
        time.sleep(delay * 0.2)
        end_time = time.time() + delay
        assert not counter.done
        count = counter.count
        if self.direction == "up":
            assert counter.start < count
            assert counter.stop > count
        else:
            assert counter.start > count
            assert counter.stop < count
        assert not counter.carry
        time.sleep(end_time - time.time())
        assert counter.done
        assert counter.count == counter.stop
        assert not counter.carry

    def test_stop_fast(self, counter, counter_defaults):
        assert not counter.done
        counter.start = 12345
        counter.step = 11
        if self.direction == "up":
            sign = 1
        else:
            sign = -1
        counter.stop = counter.start + sign * counter.step * 23
        counter.reset()
        counter.on = True
        time.sleep(0.1)
        assert counter.count == counter.stop
        assert counter.done
        assert not counter.carry


class TestCustomDownCounter(TestCustomUpCounter):
    direction = "down"

    @pytest.fixture
    def _counter(self, my_example_counter):
        return my_example_counter.custom_down_counter

    @pytest.fixture
    def counter_defaults(self, my_example_counter):
        return my_example_counter._custom_down_counter_kwargs
