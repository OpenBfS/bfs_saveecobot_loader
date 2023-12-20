# SaveEcoBot Loader Plugin

This experimental Plugin loads radiological SaveEcoBot data from their Homepage (<https://www.saveecobot.com/en/radiation-maps>) into QGIS. The Download takes several minutes, because the Plugin loads the approx. 700 measurement stations and requests the details for each of these stations resulting in about 700 single requests being sent and processed. The relevant URLs are already preconfigured, as recently working, but can be changed in case of any changes in the webpage.

## License

This Plugin is licensed under the [GPL](http://docs.geoserver.org/latest/en/user/introduction/license.html). See also LICENSE file in this repo.

## Using

This Plugin can not be installed by the official QGIS Plugin Repo using QGIS internal Plugin Manager yet, ut wil be available soon. As long as you can not find it in the official Repo (experimental!), please Download a released archive of the code and unpack it in the Plugin folder of your QGIS profile manually.

## Bugs

[Github Issuetracker](https://github.com/OpenBfS/bfs_saveecobot_loader/issues)

## Contributing

Feel free to fork this Repo and generate any PR on Github.

## Contact

Dr. Marco Lechner\
mlechner@bfs.de\
Bundesamt für Strahlenschutz │ Federal Office for Radiation Protection\
Koordination Notfallschutzsysteme │ Coordination Emergency Systems │ RN 1\

Willy-Brandt-Strasse 5\
38226 Salzgitter\
info@bfs.de\
<https://www.bfs.de>
