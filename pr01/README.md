# Практическая работа № 1 - Вариант B

## 1. Пользователи и группы
Создана группа `developers` и пользователь `student2`, добавленный в эту группу:
```text
$ sudo groupadd developers
$ sudo useradd -m -s /bin/bash student2
$ sudo usermod -aG developers student2
$ groups
raptor adm cdrom sudo dip plugdev users docker developers
```
# 2. Общий каталог /srv/shared

Настроен каталог с правами SetGID (2775), владельцем `root` и группой `developers`:
```text

$ ls -ld /srv/shared
drwxrwsr-x 2 root developers 4096 Oct 15 12:07 /srv/shared
3. Проверка прав на удаление файлов
Создан файл от имени student2 и предпринята попытка удаления от основного пользователя:
```text

$ sudo -u student2 touch /srv/shared/test_file.txt
$ ls -l /srv/shared/test_file.txt
-rw-r--r-- 1 student2 developers 0 Oct 15 12:07 /srv/shared/test_file.txt
$ rm /srv/shared/test_file.txt
rm: remove write-protected regular empty file '/srv/shared/test_file.txt'? y
rm: cannot remove '/srv/shared/test_file.txt': Permission denied
Результат: Обычный пользователь не может удалить чужой файл внутри защищенного каталога.
```
#4. Ответы на вопросы
Чем su отличается от sudo?

su (substitute user) переключает текущую сессию на другого пользователя (по умолчанию root), запрашивая пароль этого пользователя. sudo выполняет конкретную разовую команду с правами суперпользователя, используя пароль текущего пользователя.

Почему в Ubuntu по умолчанию заблокирован вход под root?

Это сделано в целях безопасности для предотвращения атак перебора пароля (brute-force) и обязательного логирования всех административных действий конкретных пользователей через sudo.

#5. Настройка ~/.bashrc
##В файл конфигурации добавлены алиасы cls, ll и переменная окружения OS_COURSE:

```text
$echo$OS_COURSE
os-design
```
