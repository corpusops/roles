# ansible plugin to DRY common routines inside corpusops roles


- Usage:
   - Add corpusops.roles/ansible_plugins to the role/meta/main.yml
   - Load the plugin via the module loader
   - use it

- Example:
```python

    class ActionModule(ActionBase):

        TRANSFERS_FILES = True

        def run(self, tmp=None, task_vars=None):
            ...
            self._ah = self._shared_loader_obj.action_loader.get(
                'cops_actionhelper',
                self._task,
                self._connection,
                self._play_context,
                self._loader,
                self._templar,
                self._shared_loader_obj)
            ret = self._ah.exec_command('ls')
            ...


```

To handle exceptions, as the module is loaded dynamicaly, you ll have to dpo something like that:

```python
     class ActionModule(ActionBase):

        TRANSFERS_FILES = True

        def run(self, tmp=None, task_vars=None):
            ...
            self._ah = self._shared_loader_obj.action_loader.get(
                'cops_actionhelper',
                self._task,
                self._connection,
                self._play_context,
                self._loader,
                self._templar,
                self._shared_loader_obj)
            try:
                ret = self._ah.which('xfoobar')
            except Exception, exc:
                klass = '{0}'.format(exc.__class__)
                if 'CommandNotFound' in klass:
                    print('catched')
                else:
                    raise(exc)
            ...
```
