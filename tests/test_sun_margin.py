from agent import path_crosses_sun, SUN_SAFE_RADIUS

def test_sun_margin():
    assert SUN_SAFE_RADIUS >= 12.0, f"Expected SUN_SAFE_RADIUS >= 12.0, got {SUN_SAFE_RADIUS}"
    src = (50.0, 20.0)
    dst = (50.0, 80.0)
    assert path_crosses_sun(src, dst) == True
    print("Sun margin test passed!")

if __name__ == "__main__":
    test_sun_margin()
