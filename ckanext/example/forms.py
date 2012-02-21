import os
import logging
from ckan.authz import Authorizer
from ckan.logic.converters import convert_to_extras,\
    convert_from_extras, convert_to_tags, convert_from_tags, free_tags_only
from ckan.logic import get_action, NotFound
from ckan.logic.schema import package_form_schema, group_form_schema
from ckan.lib.base import c, model
from ckan.plugins import IDatasetForm, IGroupForm, IConfigurer
from ckan.plugins import IGenshiStreamFilter
from ckan.plugins import implements, SingletonPlugin
from ckan.lib.navl.validators import ignore_missing, keep_extras

log = logging.getLogger(__name__)

EXAMPLE_VOCAB = u'example_vocab'


class ExampleGroupForm(SingletonPlugin):
    """This plugin demonstrates how a class packaged as a CKAN
    extension might extend CKAN behaviour by providing custom forms
    based on the type of a Group.

    In this case, we implement two extension interfaces to provide custom
    forms for specific types of group.

      - ``IConfigurer`` allows us to override configuration normally
        found in the ``ini``-file.  Here we use it to specify where the
        form templates can be found.
        
      - ``IGroupForm`` allows us to provide a custom form for a dataset
        based on the 'type' that may be set for a group.  Where the 
        'type' matches one of the values in group_types then this 
        class will be used. 
    """
    implements(IGroupForm, inherit=True)
    implements(IConfigurer, inherit=True)
    
    def update_config(self, config):
        """
        This IConfigurer implementation causes CKAN to look in the
        ```templates``` directory when looking for the group_form()
        """
        here = os.path.dirname(__file__)
        rootdir = os.path.dirname(os.path.dirname(here))
        template_dir = os.path.join(rootdir, 'ckanext',
                                    'example', 'theme', 'templates')
        config['extra_template_paths'] = ','.join([template_dir,
                config.get('extra_template_paths', '')])
            
    def group_form(self):
        """
        Returns a string representing the location of the template to be
        rendered.  e.g. "forms/group_form.html".
        """
        return 'forms/group_form.html'

    def group_types(self):
        """
        Returns an iterable of group type strings.

        If a request involving a group of one of those types is made, then
        this plugin instance will be delegated to.

        There must only be one plugin registered to each group type.  Any
        attempts to register more than one plugin instance to a given group
        type will raise an exception at startup.
        """
        return ["testgroup"]

    def is_fallback(self):
        """
        Returns true iff this provides the fallback behaviour, when no other
        plugin instance matches a group's type.

        As this is not the fallback controller we should return False.  If 
        we were wanting to act as the fallback, we'd return True
        """
        return False                
                
    def form_to_db_schema(self):
        """
        Returns the schema for mapping group data from a form to a format
        suitable for the database.
        """
        return group_form_schema()

    def db_to_form_schema(self):
        """
        Returns the schema for mapping group data from the database into a
        format suitable for the form (optional)
        """
        return {}
        
    def check_data_dict(self, data_dict):
        """
        Check if the return data is correct.

        raise a DataError if not.
        """

    def setup_template_variables(self, context, data_dict):
        """
        Add variables to c just prior to the template being rendered.
        """                
                

class ExampleDatasetForm(SingletonPlugin):
    """This plugin demonstrates how a theme packaged as a CKAN
    extension might extend CKAN behaviour.

    In this case, we implement three extension interfaces:

      - ``IConfigurer`` allows us to override configuration normally
        found in the ``ini``-file.  Here we use it to specify where the
        form templates can be found.
      - ``IDatasetForm`` allows us to provide a custom form for a dataset
        based on the type_name that may be set for a package.  Where the
        type_name matches one of the values in package_types then this
        class will be used.
    """
    implements(IDatasetForm, inherit=True)
    implements(IConfigurer, inherit=True)    
    implements(IGenshiStreamFilter)
    
    def update_config(self, config):
        """
        This IConfigurer implementation causes CKAN to look in the
        ```templates``` directory when looking for the package_form()
        """
        here = os.path.dirname(__file__)
        rootdir = os.path.dirname(os.path.dirname(here))
        template_dir = os.path.join(rootdir, 'ckanext',
                                    'example', 'theme', 'templates')
        config['extra_template_paths'] = ','.join([template_dir,
                config.get('extra_template_paths', '')])

    # def configure(self, config):
    #     '''
    #     Adds some new vocabularies to the database if they don't already exist.

    #     '''
    #     # Add a 'genre' vocabulary with some tags.
    #     self.genre_vocab = model.Vocabulary.get('Genre')
    #     if not self.genre_vocab:
    #         log.info("Adding vocab Genre")
    #         self.genre_vocab = model.Vocabulary('Genre')
    #         model.Session.add(self.genre_vocab)
    #         model.Session.commit()
    #         log.info("Adding example tags to vocab %s" % self.genre_vocab.name)
    #         jazz_tag = model.Tag('jazz', self.genre_vocab.id)
    #         soul_tag = model.Tag('soul', self.genre_vocab.id)
    #         model.Session.add(jazz_tag)
    #         model.Session.add(soul_tag)
    #         model.Session.commit()

    #     # Add a 'composer' vocabulary with some tags.
    #     self.composer_vocab = model.Vocabulary.get('Composer')
    #     if not self.composer_vocab:
    #         log.info("Adding vocab Composer")
    #         self.composer_vocab = model.Vocabulary('Composer')
    #         model.Session.add(self.composer_vocab)
    #         model.Session.commit()
    #         log.info("Adding example tags to vocab %s" %
    #                 self.composer_vocab.name)
    #         mintzer_tag = model.Tag('Bob Mintzer', self.composer_vocab.id)
    #         lewis_tag = model.Tag('Steve Lewis', self.composer_vocab.id)
    #         model.Session.add(mintzer_tag)
    #         model.Session.add(lewis_tag)
    #         model.Session.commit()

    def package_form(self):
        """
        Returns a string representing the location of the template to be
        rendered.  e.g. "package/new_package_form.html".
        """
        return 'forms/dataset_form.html'

    def is_fallback(self):
        """
        Returns true iff this provides the fallback behaviour, when no other
        plugin instance matches a package's type.

        As this is not the fallback controller we should return False.  If
        we were wanting to act as the fallback, we'd return True
        """
        return True

    def package_types(self):
        """
        Returns an iterable of package type strings.

        If a request involving a package of one of those types is made, then
        this plugin instance will be delegated to.

        There must only be one plugin registered to each package type.  Any
        attempts to register more than one plugin instance to a given package
        type will raise an exception at startup.
        """
        return ["example_dataset_form"]

    def setup_template_variables(self, context, data_dict=None):
        """
        Adds variables to c just prior to the template being rendered that can
        then be used within the form
        """
        c.licences = [('', '')] + model.Package.get_license_options()
        c.publishers = [('Example publisher', 'Example publisher 2')]
        c.is_sysadmin = Authorizer().is_sysadmin(c.user)
        c.resource_columns = model.Resource.get_columns()
        try:
            c.vocab_tags = get_action('tag_list')(context, {'vocabulary_id': EXAMPLE_VOCAB})
            # c.genre_tags = get_action('tag_list')(context, {'vocabulary_id': self.genre_vocab.name})
            # c.composer_tags = get_action('tag_list')(context, {'vocabulary_id': self.composer_vocab.name})
        except NotFound:
            c.vocab_tags = None

        ## This is messy as auths take domain object not data_dict
        pkg = context.get('package') or c.pkg
        if pkg:
            c.auth_for_change_state = Authorizer().am_authorized(
                c, model.Action.CHANGE_STATE, pkg)

    def form_to_db_schema(self):
        """
        Returns the schema for mapping package data from a form to a format
        suitable for the database.
        """
        schema = package_form_schema()
        schema.update({
            'published_by': [ignore_missing, unicode, convert_to_extras],
            'vocab_tags': [ignore_missing, convert_to_tags(EXAMPLE_VOCAB)],
            # 'genre_tags': [ignore_missing, convert_to_tags(self.genre_vocab.name)],
            # 'composer_tags': [ignore_missing, convert_to_tags(self.composer_vocab.name)],
        })
        return schema
    
    def db_to_form_schema(self):
        """
        Returns the schema for mapping package data from the database into a
        format suitable for the form (optional)
        """
        schema = package_form_schema()
        schema.update({
            'tags': {
                '__extras': [keep_extras, free_tags_only]
            },
            'vocab_tags_selected': [convert_from_tags(EXAMPLE_VOCAB), ignore_missing],
            # 'genre_tags_selected': [convert_from_tags(self.genre_vocab.name),
            #     ignore_missing],
            # 'composer_tags_selected': [
            #     convert_from_tags(self.composer_vocab.name), ignore_missing],
            'published_by': [convert_from_extras, ignore_missing],
        })
        return schema

    def check_data_dict(self, data_dict):
        """
        Check if the return data is correct and raises a DataError if not.
        """
        return

    def filter(self, stream):
        return stream

    # def filter(self, stream):
    #     # Add vocab tags to the bottom of the sidebar.
    #     from pylons import request
    #     from genshi.filters import Transformer
    #     from genshi.input import HTML
    #     routes = request.environ.get('pylons.routes_dict')
    #     if routes.get('controller') == 'package' \
    #         and routes.get('action') == 'read':
    #             for vocab in (self.genre_vocab, self.composer_vocab):
    #                 vocab_tags = [tag for tag in c.pkg_dict.get('tags', [])
    #                         if tag.get('vocabulary_id') == vocab.id]
    #                 if not vocab_tags:
    #                     continue
    #                 html = '<li class="sidebar-section">'
    #                 html = html + '<h3>%s</h3>' % vocab.name
    #                 html = html + '<ul class="tags clearfix">'
    #                 for tag in vocab_tags:
    #                     html = html + '<li>%s</li>' % tag.get('name')
    #                 html = html + "</ul></li>"
    #                 stream = stream | Transformer("//div[@id='sidebar']")\
    #                     .append(HTML(html))
    #     return stream
