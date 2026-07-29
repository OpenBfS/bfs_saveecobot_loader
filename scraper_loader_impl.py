# -*- coding: utf-8 -*-
"""SaveEcoBot loader implementation."""

import json


def run_scraper_loader(plugin):
    """Execute the existing SaveEcoBot loading workflow."""
    from qgis.PyQt.QtCore import (
        QDateTime,
        QMetaType,
        QUrl,
        QUrlQuery,
        QVariant,
        Qt,
    )
    from qgis.PyQt.QtNetwork import QNetworkRequest
    from qgis.PyQt.QtWidgets import QProgressDialog
    from qgis.core import (
        Qgis,
        QgsCoordinateReferenceSystem,
        QgsFeature,
        QgsField,
        QgsGeometry,
        QgsNetworkAccessManager,
        QgsPointXY,
        QgsProject,
        QgsVectorLayer,
    )

    requesttime = plugin.dlg.dateTimeEdit.dateTime()
    sebtimestring = requesttime.toString('yyyy-MM-ddThhmm:ss')
    sebkey = 'gamma'

    sebquery = QUrlQuery()
    sebquery.addQueryItem('date', sebtimestring)
    seburl = QUrl(plugin.dlg.sebDataUrlLineEdit.text())
    seburl.setQuery(sebquery)
    plugin.prog = QProgressDialog('Requesting data. This may take a while. Please be patient ...', 'Cancel', 0, 100)
    plugin.prog.setWindowTitle('SaveEcoBot data loader. Requesting locations.')
    plugin.prog.setWindowModality(Qt.WindowModality.WindowModal)
    plugin.prog.setMinimumWidth(500)
    plugin.prog.show()

    manager = QgsNetworkAccessManager()
    sebrequest = QNetworkRequest(seburl)
    response = manager.blockingGet(sebrequest)
    status_code = response.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
    if status_code == 200:
        sebdata = json.loads(bytes(response.content()))
    else:
        plugin.iface.messageBar().pushMessage(
            'SaveEcoBot loader error',
            "Couldn't load data from " + seburl.toString(),
            level=Qgis.Critical,
        )
        return None

    vl_name = plugin.dlg.lineEditLayerName.text() if (plugin.dlg.lineEditLayerName.text() and len(plugin.dlg.lineEditLayerName.text()) > 0) else 'temporary_saveecobot'
    vl = QgsVectorLayer('Point', vl_name, 'memory')
    vl.setCrs(QgsCoordinateReferenceSystem('EPSG:4326'))

    pr = vl.dataProvider()
    pr.addAttributes([
        QgsField('id', QMetaType.Type.Int),
        QgsField('lon', QMetaType.Type.Double),
        QgsField('lat', QMetaType.Type.Double),
    ])

    keylist = []
    if 'devices' in sebdata.keys() and isinstance(sebdata['devices'], list):
        for sebdatarow in sebdata['devices']:
            for key in sebdatarow.keys():
                if key not in keylist:
                    keylist.append(key)
                    try:
                        float(sebdatarow[key])
                        pr.addAttributes([QgsField(key, QMetaType.Type.Double)])
                    except ValueError:
                        pr.addAttributes([QgsField(key, QMetaType.Type.QString)])
    else:
        plugin.iface.messageBar().pushMessage(
            'SaveEcoBot loader error',
            'No devices list found in data from ' + seburl.toString(),
            level=Qgis.MessageLevel.Critical,
        )
        plugin.prog.close()
        return None

    vl.updateFields()

    if 'devices' in sebdata.keys() and isinstance(sebdata['devices'], list):
        for sebdatarow in sebdata['devices']:
            if sebkey in sebdatarow:
                feat = QgsFeature()
                feat.setFields(vl.fields())
                feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(float(sebdatarow['n']), float(sebdatarow['a']))))
                featattributes = []
                for key in feat.fields().names():
                    if key == 'id':
                        featattributes.append(int(sebdatarow['i']))
                    if key == 'lon':
                        featattributes.append(float(sebdatarow['a']))
                    if key == 'lat':
                        featattributes.append(float(sebdatarow['n']))
                for key in feat.fields().names():
                    if key not in ('id', 'device_id', 'lon', 'lat'):
                        if key in sebdatarow:
                            if vl.fields().field(key).type() == QVariant.Int:
                                try:
                                    featattributes.append(int(sebdatarow[key]))
                                except Exception:
                                    featattributes.append(None)
                                    plugin.iface.messageBar().pushMessage(
                                        'Warning',
                                        'wrong data type at id ' + str(featattributes[0]) + ' for attribute ' + key + '. value ' + str(sebdatarow[key]) + ' not imported.',
                                        level=Qgis.MessageLevel.Warning,
                                    )
                            elif vl.fields().field(key).type() == QVariant.Double:
                                try:
                                    featattributes.append(float(sebdatarow[key]))
                                except Exception:
                                    featattributes.append(None)
                                    plugin.iface.messageBar().pushMessage(
                                        'Warning',
                                        'wrong data type at id ' + str(featattributes[0]) + ' for attribute ' + key + '. value ' + str(sebdatarow[key]) + ' not imported.',
                                        level=Qgis.MessageLevel.Warning,
                                    )
                            elif vl.fields().field(key).type() == QVariant.String:
                                try:
                                    featattributes.append(str(sebdatarow[key]))
                                except Exception:
                                    featattributes.append(None)
                                    plugin.iface.messageBar().pushMessage(
                                        'Warning',
                                        'wrong data type at id ' + str(featattributes[0]) + ' for attribute ' + key + '. value ' + str(sebdatarow[key]) + ' not imported.',
                                        level=Qgis.MessageLevel.Warning,
                                    )
                            else:
                                featattributes.append(None)
                        else:
                            featattributes.append(None)
                if len(featattributes) == len(vl.fields()):
                    feat.setAttributes(featattributes)
                    pr.addFeatures([feat])
                else:
                    plugin.iface.messageBar().pushMessage(
                        'Error',
                        'featattributes len for id ' + str(featattributes[0]) + ' is ' + str(len(featattributes)),
                        level=Qgis.MessageLevel.Critical,
                    )

    vl.updateExtents()
    QgsProject.instance().addMapLayer(vl)
    if 'last_updated_at' in sebdata.keys() and 'gamma' in sebdata['last_updated_at']:
        vlm = vl.metadata()
        vlm.setAbstract('gamma latest updated (Ukraine local time): ' + sebdata['last_updated_at']['gamma'])
        vl.setMetadata(vlm)
    plugin.iface.mapCanvas().refresh()

    pr.addAttributes([
        QgsField('device_id', QMetaType.Type.QString),
        QgsField('latest', QMetaType.Type.QDateTime),
        QgsField('history', QMetaType.Type.QString),
        QgsField('history_hours', QMetaType.Type.Int),
        QgsField('content', QMetaType.Type.QString),
        QgsField('payload_device', QMetaType.Type.QString),
        QgsField('payload_location', QMetaType.Type.QString),
        QgsField('payload_platform', QMetaType.Type.QString),
        QgsField('payload_value', QMetaType.Type.QString),
        QgsField('payload', QMetaType.Type.QString),
    ])
    vl.updateFields()
    vl.startEditing()

    marker_url_template = plugin.dlg.sebMarkerDataUrlLineEdit.text().strip()
    if '{sfid}' not in marker_url_template:
        marker_url_template = marker_url_template.rstrip('/') + '/{sfid}/gamma.json'

    count = vl.featureCount()
    plugin.prog.setWindowTitle('SaveEcoBot details loader. Requesting ' + str(count) + ' details.')

    for current, feature in enumerate(vl.getFeatures()):
        markerdata = {}
        tried = 0
        maxtry = 3
        sfid = str(feature.attribute('id'))
        percent = current / float(count) * 100
        plugin.prog.setValue(int(percent))
        plugin.prog.setLabelText('Requesting details for device ID ' + sfid + '. Please be patient.')
        markerurl = QUrl(marker_url_template.replace('{sfid}', sfid))
        markerrequest = QNetworkRequest(markerurl)
        while tried <= maxtry:
            response = manager.blockingGet(markerrequest)
            status_code = response.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
            if status_code == 200:
                markerdata = json.loads(bytes(response.content()))
                break
            elif status_code != 200 and (tried < maxtry):
                tried += 1
                plugin.iface.messageBar().pushMessage(
                    'SaveEcoBot loader error',
                    'Retrying to load details for ' + sfid + '. Tried ' + str(tried) + '/' + str(maxtry),
                    level=Qgis.MessageLevel.Info,
                )
                continue
            else:
                plugin.iface.messageBar().pushMessage(
                    'SaveEcoBot loader error',
                    'Could not load details for ' + sfid + '. Giving up after ' + str(tried) + ' tries.',
                    level=Qgis.MessageLevel.Warning,
                    duration=3,
                )
                continue
        feature.setAttribute('device_id', str(markerdata['marker_data']['id']))
        if len(markerdata['history']) > 0:
            sorted_history = sorted(markerdata['history'], key=lambda x: x[0])
            feature.setAttribute('latest', QDateTime.fromString(sorted_history[-1][0], 'yyyy-MM-ddThh:mm:ssZ'))
            feature.setAttribute('history', str(markerdata['history']))
        feature.setAttribute('history_hours', int(markerdata['history_hours']))
        feature.setAttribute('content', str(markerdata['payload']))
        feature.setAttribute('payload_device', str(markerdata['payload']['device']))
        feature.setAttribute('payload_location', str(markerdata['payload']['location']))
        feature.setAttribute('payload_platform', str(markerdata['payload']['platform']))
        feature.setAttribute('payload_value', str(markerdata['payload']['value']))
        feature.setAttribute('payload', str(markerdata['payload']))
        vl.updateFeature(feature)
        percent = current / float(count) * 100
        plugin.prog.setValue(int(percent))
        plugin.prog.setLabelText('Requesting details for device ID ' + sfid + '. Please be patient.')
        if plugin.prog.wasCanceled():
            break
    vl.commitChanges()

    ltroot = QgsProject.instance().layerTreeRoot()
    ltlayer = ltroot.findLayer(vl.id())
    ltlayer.setCustomProperty('showFeatureCount', True)

    plugin.prog.close()
    plugin.iface.mapCanvas().refresh()
    return vl
