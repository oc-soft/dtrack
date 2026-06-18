import dtrack 
import sys
import json


class TestApp:

    def __init__(self):
        self._command_hdlr = {
            'init': self.dtrack_init,
            'create': self.dtrack_create,
            'update': self.dtrack_update,
            'update-header': self.dtrack_update_header,
            'edit': self.dtrack_edit,
            'commit': self.dtrack_commit,
            'history': self.dtrack_history,
            'trees': self.dtrack_trees,
            'items': self.dtrack_items,
            'content': self.dtrack_content,
            'header': self.dtrack_header,
            'content-history': self.dtrack_content_history,
            'header-history': self.dtrack_header_history,
            'list-content-id': self.dtrack_list_content_id,
            'list-editing-content-id': self.dtrack_list_editing_content_id
        }

    @property
    def command_handler(self):
        return self._command_hdlr
    @property
    def dtrack_app(self):
        if not hasattr(self, "_dtrack_app"):
            app = dtrack.App()
            app.load_from_env()
            self._dtrack_app = app
        return self._dtrack_app
 
    def run(self, **command_params):
        self.command_handler[command_params['command']](**command_params)

    def dtrack_init(self, **params):
        self.dtrack_app.init_system()

    def dtrack_create(self, **params):
        content_id = self.dtrack_app.create_content_for_editing()
        print(content_id)

    def dtrack_update(self, **params):
        if params['content_id']:
            if len(params['params']):
                with open(params['params'][-1], "rb") as new_content:
                    self.dtrack_app.update_content(
                            params['content_id'], new_content)
            else:
                self.dtrack_app.update_content(
                        params['content_id'], sys.stdin.buffer)
                
    def dtrack_update_header(self, **params):
        if params['content_id']:
            if len(params['params']):
                with open(params['params'][-1], "r") as fp:
                    self.dtrack_app.update_header(
                            params['content_id'], json.load(fp))
            else:
                self.dtrack_app.update_header(
                        params['content_id'], json.load(sys.stdin))

    def dtrack_edit(self, **params):
        if params['content_id']:
            self.dtrack_app.create_edit_content_from_id(params['content_id'])

    def dtrack_commit(self, **params):
        if params['content_id'] and params['author'] and params['email']:
            self.dtrack_app.commit(
                    params['content_id'], params['delete'],
                    params['author'], params['email'])

    def dtrack_content(self, **params):
        if params['content_id']: 
            if params['mode'] != 'edit':
                self.dtrack_app.get_content(
                    params['content_id'], 
                    sys.stdout.buffer)
            else:
                self.dtrack_app.get_content_editing(
                    params['content_id'], 
                    sys.stdout.buffer)
 
    def dtrack_header(self, **params):
        if params['content_id']:
            if params['mode'] != 'edit':
                print(json.dumps(self.dtrack_app.get_header(
                    params['content_id']).header, indent=2))
            else: 
                print(json.dumps(self.dtrack_app.get_header_editing(
                    params['content_id']).header, indent=2))

    def dtrack_history(self, **params):
        self.iterate_commit(**params)

    def iterate_commit(self, **params):
        for commit in self.dtrack_app.iterate_commit():
            print(json.dumps(commit, indent=2)) 

    def dtrack_trees(self, **params):
        for tree in self.dtrack_app.iterate_commit_tree(): 
            print(tree) 

    def dtrack_items(self, **params):
        first_tree = None
        for tree in self.dtrack_app.iterate_commit_tree():
            first_tree = tree
            break
        if first_tree is not None:
            for item in self.dtrack_app.iterate_tree_items(first_tree):
                print(json.dumps(item, indent=2))
            
    def dtrack_content_history(self, **params):
        if params['content_id']:
            for oid in self.dtrack_app.iterate_history_of_id(
                    params['content_id']):
                self.dtrack_app.get_content_from_oid(
                        oid, sys.stdout.buffer)
    def dtrack_header_history(self, **params):
        if params['content_id']:
            for oid in self.dtrack_app.iterate_history_of_id(
                    params['content_id']):
                print(json.dumps(
                    self.dtrack_app.get_header_from_oid(oid).header,
                    indent=2))
    def dtrack_list_content_id(self, **params):
        print(
            json.dumps(
                [x for x in self.dtrack_app.list_content_id()],
                indent=2))

    def dtrack_list_editing_content_id(self, **params):
        print(
            json.dumps(
                [x for x in self.dtrack_app.list_editing_content_id()],
                indent=2))


if __name__ == "__main__":
    from argparse import ArgumentParser
    argparse = ArgumentParser()
    argparse.add_argument('-i', '--id', type=int)
    argparse.add_argument('-d', '--delete', action='store_true')       
    argparse.add_argument('-m', '--email', type=str)
    argparse.add_argument('-a', '--author', type=str)
    argparse.add_argument(
            '-e', '--mode', type=str,
            choices=['release', 'edit'], default='release')
    argparse.add_argument(
            'command', type=str,
            choices=[
                'init', 'create', 'update', 'update-header',
                'edit', 'commit', 'history', 'trees', 'items',
                'content', 'header',
                'content-history', 'header-history',
                'list-content-id', 'list-editing-content-id'],
            nargs='?')
    
    argparse.add_argument(
            'command_params', nargs='*')

    args = argparse.parse_args()
    TestApp().run(
            command=args.command,
            params=args.command_params,
            content_id=args.id,
            delete=args.delete,
            author=args.author,
            email=args.email,
            mode=args.mode)
    pass

# vi: se ts=4 sw=4 et:
