# tool-stack-optima 5大通用动词契约
default:
    @just --list

setup:
    @python main.py setup

run prompt="":
    @python main.py run "{{prompt}}"

test:
    @python main.py test

health:
    @python main.py health

clean:
    @python main.py clean

languages:
    @python main.py languages
