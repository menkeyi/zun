
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from oslo_log import log as logging
from oslo_utils import fileutils

from zun.common import exception
from zun.common.i18n import _
import zun.conf
from zun.image import driver
from zun.image.glance import utils

CONF = zun.conf.CONF

LOG = logging.getLogger(__name__)


class GlanceDriver(driver.ContainerImageDriver):

    def __init__(self):
        super(GlanceDriver, self).__init__()

    def pull_image(self, context, image_name):
        LOG.debug('Pulling image from glance %s' % image_name)
        try:
            glance = utils.create_glanceclient(context)
            image_meta = utils.find_image(context, image_name)
            LOG.debug('Image %s was found in glance, downloading now...'
                      % image_name)
            image_chunks = glance.images.data(image_meta.id)
        except exception.ImageNotFound:
            LOG.error('Image %s was not found in glance' % image_name)
            raise
        except Exception as e:
            msg = _('Cannot download image from glance: {0}')
            raise exception.ZunException(msg.format(e))
        try:
            images_directory = CONF.glance.images_directory
            fileutils.ensure_tree(images_directory)
            out_path = os.path.join(images_directory, image_meta.id + '.tar')
            with open(out_path, 'wb') as fd:
                for chunk in image_chunks:
                    fd.write(chunk)
        except Exception as e:
            msg = _('Error occured while writing image: {0}')
            raise exception.ZunException(msg.format(e))
        LOG.debug('Image %s was downloaded to path : %s'
                  % (image_name, out_path))
        return {'image': image_name, 'path': out_path}
