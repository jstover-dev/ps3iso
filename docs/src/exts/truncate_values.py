from sphinx.ext.autodoc import DataDocumenter, ModuleLevelDocumenter, SUPPRESS
from sphinx.util.inspect import object_description

from ps3iso.sfo.parameters import VALID_SFO_PARAMETERS

# List of objects which wil have their value descriptions truncated
TRUNCATE_DOC_OBJECTS = [
    VALID_SFO_PARAMETERS,
]

# Maximum length of a value description before ellipsis are added
TRUNCATE_DOC_LENGTH = 50


def add_directive_header(self, sig):
    ModuleLevelDocumenter.add_directive_header(self, sig)
    if not self.options.annotation:
        try:
            objrepr = object_description(self.object)

            if self.object in TRUNCATE_DOC_OBJECTS:
                objrepr = objrepr[:TRUNCATE_DOC_LENGTH] + "..."

        except (ValueError, KeyError):
            pass
        else:
            self.add_line(u'   :annotation: = ' + objrepr, '<autodoc>')

    elif self.options.annotation is not SUPPRESS:
        self.add_line(u'   :annotation: %s' % self.options.annotation,
                      '<autodoc>')


def setup(app):
    DataDocumenter.add_directive_header = add_directive_header
