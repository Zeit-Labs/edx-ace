from abc import ABCMeta

import attr
import six
from django.template import loader
from edx_ace.channel import ChannelType


@six.add_metaclass(ABCMeta)
class AbstractRenderer(object):
    """
    Base class for message renderers.

    A message renderer is responsible for taking a one, or more, templates, and context, and outputting
    a rendered message for a specific message channel (e.g. email, SMS, push notification).
    """
    rendered_message_cls = None

    def render(self, message):
        """
        Renders the given message.

        Args:
             message (Message)

         Returns:
             dict: Mapping of template names/types to rendered text.
        """
        rendered = {}
        for attribute in attr.fields(self.rendered_message_cls):
            field = attribute.name
            if field.endswith('_html'):
                filename = field.replace('_html', '.html')
            else:
                filename = field + '.txt'
            template = self.get_template_for_message(message, filename)
            rendered[field] = template.render(message.context)

        return self.rendered_message_cls(**rendered)

    def get_template_for_message(self, message, filename):
        template_path = "{msg.app_label}/edx_ace/{msg.name}/{channel.value}/{filename}".format(
            msg=message,
            channel=self.channel,
            filename=filename,
        )
        return loader.get_template(template_path)


@attr.s
class RenderedEmail(object):
    from_name = attr.ib()
    subject = attr.ib()
    body_html = attr.ib()
    head_html = attr.ib()
    body = attr.ib()


class EmailRenderer(AbstractRenderer):
    channel = ChannelType.EMAIL
    rendered_message_cls = RenderedEmail
