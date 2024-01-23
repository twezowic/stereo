# Renderer stereo
Prowadzący: dr inż. Łukasz Dąbała

W ramach projektu należy stworzyć program, który będzie umożliwiał rendering obrazów stereo. W tym celu należy zaimplementować:
1. wsparcie dla różnego typu plików wejściowych z modelem 3D:
    * obj
    * alembic
2. cieniowanie Phonga
3. interpretację właściwości materiału: diffuse, specular
4. wsparcie dla tekstur typu diffuse, specular
5. wsparcie dla świateł punktowych - możliwość dodawania nowych, edycja właściwości światła
6. kamerę perspektywiczną - możliwość poruszania się po scenie oraz obrotu
7. kamerę stereo pracującą w różnych trybach i dającą możliwość sposobu trybu stereo. Kamera powinna umożliwiać ustawienie m.in. takich właściwości jak odległość oczu.
    * tryb równoległy - kamery mają równoległe osie widoku
    * tryb zbieżny - osie widoku kamer przetną się. Miejsce przecięcia powinno być możliwe do ustawienia
8. zapisanie wyników do plików graficznych
    * pojedyncze obrazy dla każdego z oczu
    * anaglif (przynajmniej red-cyan)
    * przelot (obraz przeznaczony dla monitorów z filtrem polaryzacyjnym)


# Obsługa

WSAD - poruszanie się
QE - góra/dół
Myszka - obrót kamery
Spacja - zmiana trybu kamery między (anaglif,stereo,przeplot)
RT - zmiana kąta zbieżności oczu
KL - zmiana rozstawu oczu
M - zapisanie zdjęcia
O - wyłączenie anaglifu