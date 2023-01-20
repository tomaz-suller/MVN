from mvn_simulator.register import Register


def test_valid():
    register = Register(0)
    assert register.value == 0
    assert register.get_value() == 0


def test_default_value():
    register = Register()
    assert register.value == 0
    assert register.get_value() == 0


def test_valid_init_value():
    register = Register(0xF)
    assert register.value == 0xF
    assert register.get_value() == 0xF


def test_init_overflow():
    register = Register(0x10000)
    assert register.value == 0


def test_setter_overflow():
    register = Register(0)
    register.value = 0x10000
    assert register.value == 0


def test_most_significant_byte():
    register = Register(0xFF0F)
    assert register.most_significant == 0xFF


def test_least_significant_byte():
    register = Register(0xFF0F)
    assert register.least_significant == 0x0F
