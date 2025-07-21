from pytest_bdd import given, then

@given("dummy step")
def dummy_step():
    print("[DEBUG] Dummy step executado (arquivo dedicado)")

@then("dummy result")
def dummy_result():
    print("[DEBUG] Dummy result executado (arquivo dedicado)")
