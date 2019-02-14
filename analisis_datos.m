close all; clear all; clc;

%% Parámetros
Channel_1_ID = 697382;
Channel_2_ID = 697383;
CantDatos = 3;

%% Variables
contador = 1;

%% Programa cíclico
while true
    %% Importar datos del último minuto
    % https://es.mathworks.com/help/thingspeak/thingspeakread.html#bvio0ym
    [canal1, timestamps1] = thingSpeakRead(Channel_1_ID, 'Fields', [1,2],...
        'NumPoints', CantDatos);
    [canal2, timestamps2] = thingSpeakRead(Channel_2_ID, 'Fields', [1,2],...
        'NumPoints', CantDatos);
    
    [x1 y1] = size(canal1);
    [x2 y2] = size(canal2);
    
    if x1 > x2
        varAux = x1;
    else
        varAux = x2;
    end
    
    % Se juntan todos los datos en una sola matriz. Además, se crea otra matriz
    % para unificar todos los timestamps
    for j = 1:varAux
        r = (j * 2) - 1;
        s = j * 2;
        
        % Se ordenan los datos teniendo en cuenta el momento en el que han sido
        % recividos en ThingSpeak (en las variables timestamps). Además,
        % primero se asegura de que el dato existe.
        if j <= x1
            if j <= x2
                if timestamps1(j) < timestamps2(j)
                    data(r, :) = canal1(j, :);
                    data(s, :) = canal2(j, :);
                    timestamps(r, :) = timestamps1(j, :);
                    timestamps(s, :) = timestamps2(j, :);
                else
                    data(r, :) = canal2(j, :);
                    data(s, :) = canal1(j, :);
                    timestamps(r, :) = timestamps2(j, :);
                    timestamps(s, :) = timestamps1(j, :);
                end
            else
                data(r, :) = canal1(j, :);
                timestamps(r, :) = timestamps1(j, :);
            end
            
        elseif j <= x2
            data(r, :) = canal2(j, :);
            timestamps(r, :) = timestamps2(j, :);
        end
    end
    
    % Se borran las variables innecesarias por claridad y ahorrar espacio
    clear canal1 canal2 timestamps1 timestamps2 x1 x2 y1 y2 varAux j r s;
    
    %% Graficar los datos obtenidos
    figure(1);
    
    subplot(2, 1, 1);
    plot(timestamps, data(:, 1), 'r-o');
    grid on;
    title('Temperatura (ºC)', 'FontSize', 12, 'FontWeight', 'Bold');
    xlabel('Fecha', 'FontWeight', 'Bold');
    tempMax = max(data(:, 1));
    tempMin = min(data(:, 1));
    ylim([tempMin-5 tempMax+5]);
    
    subplot(2, 1, 2);
    plot(timestamps, data(:, 2), '-o');
    grid on;
    title('Humedad (%)', 'FontSize', 12, 'FontWeight', 'Bold');
    xlabel('Fecha', 'FontWeight', 'Bold');
    humMax = max(data(:, 2));
    humMin = min(data(:, 2));
    ylim([humMin-5 humMax+5]);
    
    %% Climatizador
    % ultTemp = 40;
    % ultHum = 55;
    tiempo = contador;
%     tiempo = timestamps(end);
    mediaTemp = mean(data(:, 1));
    mediaHum = mean(data(:, 2));
    TempHum = [tiempo mediaTemp mediaHum];
    
    % Tabla de variables de las entradas
    Tiempo(contador) = TempHum(1);
    Temp(contador) = TempHum(2);
    Hum(contador) = TempHum(3);
    
    % Ejecutar el archivo Simulink del controlador fuzzy
    sim('ControlClimatizador.slx.r2014a');
    
    % Guardar las variables de salida en tablas
    Calefactor(contador) = salida.Data(1,1);
    Humidificador(contador) = salida.Data(1,2);
    Intercambiador(contador) = salida.Data(1,3);
    
    % Graficar los resultados y las entradas
    figure(2);
    
    subplot(3, 1, 1);
    plot(Tiempo, Temp, 'r-o');
    grid on;
    title('Temperatura (ºC)', 'FontSize', 12, 'FontWeight', 'Bold');
    xlabel('Fecha', 'FontWeight', 'Bold');
    tempMax = max(data(:, 1));
    tempMin = min(data(:, 1));
    ylim([tempMin-5 tempMax+5]);
    
    subplot(3, 1, 2);
    plot(Tiempo, Hum, '-o');
    grid on;
    title('Humedad (%)', 'FontSize', 12, 'FontWeight', 'Bold');
    xlabel('Fecha', 'FontWeight', 'Bold');
    humMax = max(data(:, 2));
    humMin = min(data(:, 2));
    ylim([humMin-5 humMax+5]);
    
    subplot(3, 1, 3);
    % stairs(Tiempo, Calefactor, Tiempo, Humidificador, Tiempo, Intercambiador);
    hold on;
    stairs(Tiempo, Calefactor)
    stairs(Tiempo, Humidificador)
    stairs(Tiempo, Intercambiador)
    grid on;
    title('Señal de Control (%)', 'FontSize', 12, 'FontWeight', 'Bold');
    xlabel('Fecha', 'FontWeight', 'Bold');
    legend('Calefactor', 'Humidificador', 'Intercambiador de Calor');
    ylim([0 100]);
    
    contador = contador + 1;
    
    pause(10);
end