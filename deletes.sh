#!/bin/bash

### git remote prune origin


# Получить список веток, которых уже нет на внешнем сервере
missing_branches=$(git branch -vv | grep ': gone]' | awk '{print $1}')

# Удалить каждую локальную ветку, у которой удалена её вышестоящая ветка.
for branch in $missing_branches; do
    git branch -D $branch
done