#include <AFMotor.h>
#include <GFButton.h>

AF_DCMotor motor_cd(1);
AF_DCMotor motor_impressora(2);
AF_DCMotor motor_costura(3);
AF_DCMotor escova(4);
bool estado_cd = true;
bool estado_impressora = true;
GFButton botao1(52);
GFButton botao2(53);
unsigned long tempoAnterior = 0;
unsigned long tempoDelay = 200;  // Tempo de atraso em milissegundos
String texto="";
int RPWM_Output = 9;  // Arduino PWM output pin 5; connect to IBT-2 pin 1 (RPWM)
int LPWM_Output = 10;  // Arduino PWM output pin 6; connect to IBT-2 pin 2 (LPWM)

int forwardPWM = 130;  // Initial speed for forward direction (0 to 255)
void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  botao1.setReleaseHandler(botao1_pressionado);
  botao2.setReleaseHandler(botao2_pressionado);
  escova.setSpeed(120);  // Inicia com a velocidade 120
  escova.run(RELEASE);   // Garante que o motor não esteja em movimento
   pinMode(RPWM_Output, OUTPUT);
  pinMode(LPWM_Output, OUTPUT);

}
void botao1_pressionado (GFButton& botao) {
  motor_impressora.run(RELEASE);
  Serial.println("Botão 1 foi pressionado e a impressora desligada");
}
void botao2_pressionado (GFButton& botao) {
  motor_impressora.run(RELEASE);
  Serial.println("Botão 2 foi pressionado e a impressora desligada");
}
void batida1_cd()
{
  motor_cd.setSpeed(255);
  motor_cd.run(FORWARD);
}
void batida2_cd()
{
  motor_cd.setSpeed(255);
  motor_cd.run(BACKWARD);
}
void batida3_impressora()
{
  motor_impressora.setSpeed(255);
  motor_impressora.run(FORWARD);
}
void batida4_impressora()
{
  motor_impressora.setSpeed(255);
  motor_impressora.run(BACKWARD);
}
void MotorCosturaBPM(int bpm) {
  int velocidade = (bpm + 6.65) / 0.89; // Fórmula para calcular a velocidade
  if (velocidade > 184) velocidade = 184; // Limita ao máximo permitido
  if (velocidade < 0) velocidade = 0;     // Limita ao mínimo permitido
  motor_costura.setSpeed(velocidade);
  motor_costura.run(FORWARD);
  Serial.print("Velocidade ajustada: ");
  Serial.print(velocidade);
  Serial.print(" (BPM: ");
  Serial.print(bpm);
  Serial.println(")");
}
void batida5_costura()//6.5V
{
  motor_costura.setSpeed(184);
  motor_costura.run(FORWARD);
}
void batida6_costura()//6V
{
  motor_costura.setSpeed(170);
  motor_costura.run(FORWARD);
}
void batida7_costura()//5.5V
{
  motor_costura.setSpeed(156);
  motor_costura.run(FORWARD);
}
void batida8_costura()
{
  motor_costura.setSpeed(142);//5V
  motor_costura.run(FORWARD);
}
void batida9_costura()//4.5V
{
  motor_costura.setSpeed(128);
  motor_costura.run(FORWARD);
}

void batida10_costura()//4V
{
  motor_costura.setSpeed(113);
  motor_costura.run(FORWARD);
}


void loop() {
  // put your main code here, to run repeatedly:
  botao1.process();
  botao2.process();
  if (Serial.available() > 0) {
    String texto_recebido = Serial.readStringUntil('\n');
    texto_recebido.trim();
    if (texto_recebido == "batida_E") {
      if (estado_cd) {
        batida1_cd();
        Serial.println("cd indo");
      }
      else {
        batida2_cd();
        Serial.println("cd voltando");
      }
      estado_cd = !estado_cd;
    }
    if (texto_recebido == "batida_D") {
      if (estado_impressora) {
        batida3_impressora();
        Serial.println("impressora indo");
      }
      else {
        batida4_impressora();
        Serial.println("impressora voltando");
      }
      estado_impressora = !estado_impressora;
    }
    if (texto_recebido.startsWith("bpm:")) {
      int bpm = texto_recebido.substring(4).toInt(); // Extrai o valor de BPM após "bpm:"
      MotorCosturaBPM(bpm);
    }
    if (texto_recebido == "batida3") {
      batida5_costura();
      Serial.println("velocidade motor 184 costura 6.5V e 152bpm");
    }
    if (texto_recebido == "batida4") {
      batida6_costura();
      Serial.println("velocidade motor 170 costura 6V e 145bpm");
    }
    if (texto_recebido == "batida5") {
      batida7_costura();
      Serial.println("velocidade motor 156 costura 5.5V e 136bpm");
    }
    if (texto_recebido == "batida6") {
      batida8_costura();
      Serial.println("velocidade motor  142 costura 5V minimo para inicio e 124bpm");
    }
    if (texto_recebido == "batida7") {
      batida9_costura();
      Serial.println("velocidade motor 128 costura 4.5V e 106bpm");
    }
    if (texto_recebido == "batida8") {
      batida10_costura();
      Serial.println("velocidade motor 113 costura 4V e 90bpm");
    }
    

    if (texto_recebido == "desliga") {
      motor_cd.run(RELEASE);
      motor_impressora.run(RELEASE);
      motor_costura.run(RELEASE);
      Serial.println("desligou");
    }
        tempoAnterior = millis();

    if (texto_recebido == "nota_on_escova_C") {
      escova.setSpeed(120);  // Inicializa em 120
      escova.run(FORWARD);
    } else if (texto_recebido == "nota_on_escova_D") { //
      escova.setSpeed(120);  // Inicializa em 120
      escova.run(FORWARD);   // Faz o motor se mover para frente
    } else if (texto_recebido == "nota_on_escova_E") {
      escova.setSpeed(120);  // Ajusta para a velocidade de E
      escova.run(FORWARD);   // Faz o motor se mover para frente
    } else if (texto_recebido == "nota_on_escova_F") {
      escova.setSpeed(120);  // Inicializa em 120
      escova.run(FORWARD);
    } else if (texto_recebido == "nota_on_escova_G") { //
      escova.setSpeed(120);  // Inicializa em 120
      escova.run(FORWARD);
    } else if (texto_recebido == "nota_on_escova_A") { //
      escova.setSpeed(120);  // Inicializa em 120
      escova.run(FORWARD);
    } else if (texto_recebido == "nota_on_escova_B") { //
      escova.setSpeed(120);  // Inicializa em 120
      escova.run(FORWARD);   // Faz o motor se mover para frente
    } else if (texto_recebido == "nota_on_escova_C#") { //
      escova.setSpeed(120);  // Inicializa em 120
      escova.run(FORWARD);
    } else if (texto_recebido == "nota_on_escova_D#") { //
      escova.setSpeed(120);  // Inicializa em 120
      escova.run(FORWARD);
    } else if (texto_recebido == "nota_on_escova_F#") { //
      escova.setSpeed(120);  // Inicializa em 120
      escova.run(FORWARD);
    } else if (texto_recebido == "nota_on_escova_G#") { //
      escova.setSpeed(120);  // Inicializa em 120
      escova.run(FORWARD);
        } else if (texto_recebido == "nota_on_escova_A#") { //
      escova.setSpeed(120);  // Inicializa em 120
      escova.run(FORWARD);
    } else if (texto_recebido == "nota_off_escova_C" || texto_recebido == "nota_off_escova_D" || texto_recebido == "nota_off_escova_E" || texto_recebido == "nota_off_escova_F" ||  texto_recebido == "nota_off_escova_G" || texto_recebido == "nota_off_escova_A" || texto_recebido == "nota_off_escova_B" || texto_recebido == "nota_off_escova_C#" || texto_recebido == "nota_off_escova_D#" || texto_recebido == "nota_off_escova_F#" || texto_recebido == "nota_off_escova_G#"|| texto_recebido == "nota_off_escova_A#") {
      escova.run(RELEASE);  // Desliga o motor
    }
    texto=texto_recebido;
     // Se receber o comando para mover o motor para frente (nota_on_liqui_B)
    if (texto_recebido == "nota_on_liqui_D") {
      forwardPWM = 120;
      analogWrite(RPWM_Output, forwardPWM);  // Define a direção para frente
      analogWrite(LPWM_Output, 0);           // Desliga o LPWM para o movimento para frente
    }
    // Se receber o comando para mover o motor para frente (nota_on_liqui_A)
    else if (texto_recebido == "nota_on_liqui_C") {
      forwardPWM = 110;
      analogWrite(RPWM_Output, forwardPWM);  // Define a direção para frente
      analogWrite(LPWM_Output, 0);           // Desliga o LPWM para o movimento para frente
    }
    // Se receber o comando para mover o motor para frente (nota_on_liqui_G)
    else if (texto_recebido == "nota_on_liqui_B") {
      forwardPWM = 155; // 160
      analogWrite(RPWM_Output, forwardPWM);  // Define a direção para frente
      analogWrite(LPWM_Output, 0);           // Desliga o LPWM para o movimento para frente
    }
        // Se receber o comando para mover o motor para frente (nota_on_liqui_G)
    else if (texto_recebido == "nota_on_liqui_A") {
      forwardPWM = 145; // 110
      analogWrite(RPWM_Output, forwardPWM);  // Define a direção para frente
      analogWrite(LPWM_Output, 0);           // Desliga o LPWM para o movimento para frente
    }
        // Se receber o comando para mover o motor para frente (nota_on_liqui_G)
    else if (texto_recebido == "nota_on_liqui_F") {
      forwardPWM = 130;
      analogWrite(RPWM_Output, forwardPWM);  // Define a direção para frente
      analogWrite(LPWM_Output, 0);           // Desliga o LPWM para o movimento para frente
    }
    else if (texto_recebido == "nota_on_liqui_G") {
      forwardPWM = 135;
      analogWrite(RPWM_Output, forwardPWM);  // Define a direção para frente
      analogWrite(LPWM_Output, 0);           // Desliga o LPWM para o movimento para frente
    }
        // Se receber o comando para mover o motor para frente (nota_on_liqui_G)
    else if (texto_recebido == "nota_on_liqui_E") {
      forwardPWM = 125;
      analogWrite(RPWM_Output, forwardPWM);  // Define a direção para frente
      analogWrite(LPWM_Output, 0);           // Desliga o LPWM para o movimento para frente
    }
    // Se o comando for para desligar o motor
    else if (texto_recebido == "nota_off_liqui_C" ||texto_recebido == "nota_off_liqui_D" || texto_recebido == "nota_off_liqui_E" || texto_recebido == "nota_off_liqui_F" ||texto_recebido == "nota_off_liqui_A" || texto_recebido == "nota_off_liqui_B" || texto_recebido == "nota_off_liqui_G") {
      forwardPWM = 0;
      analogWrite(RPWM_Output, forwardPWM);  // Desliga o motor, parando o movimento
      analogWrite(LPWM_Output, forwardPWM);  // Desliga o motor
    }
  }
  // Usando millis() para controlar os atrasos sem bloquear o código
  if (millis() - tempoAnterior >= tempoDelay) {
    if (texto == "nota_on_escova_C") {
      escova.setSpeed(75);  // Altera para a velocidade de C
      escova.run(FORWARD);  // Faz o motor se mover para frente
    } else if (texto == "nota_on_escova_D") {
      escova.setSpeed(85);  // Altera para a velocidade de F
      escova.run(FORWARD);  // Faz o motor se mover para frente
    } else if (texto == "nota_on_escova_E") {
      escova.setSpeed(95);  // Altera para a velocidade de F
      escova.run(FORWARD);  // Faz o motor se mover para frente
    } else if (texto == "nota_on_escova_F") {
      escova.setSpeed(100);  // Altera para a velocidade de A
      escova.run(FORWARD);  // Faz o motor se mover para frente
    } else if (texto == "nota_on_escova_G") {
      escova.setSpeed(110);  // Altera para a velocidade de B
      escova.run(FORWARD);  // Faz o motor se mover para frente
    } else if (texto == "nota_on_escova_A") {
      escova.setSpeed(120);  // Altera para a velocidade de F
      escova.run(FORWARD);  // Faz o motor se mover para frente
    } else if (texto == "nota_on_escova_B") {
      escova.setSpeed(135);  // Altera para a velocidade de F
      escova.run(FORWARD);  // Faz o motor se mover para frente
    } else if (texto == "nota_on_escova_C#") {
      escova.setSpeed(80);  // Altera para a velocidade de F
      escova.run(FORWARD);  // Faz o motor se mover para frente
    } else if (texto == "nota_on_escova_D#") {
      escova.setSpeed(90);  // Altera para a velocidade de F
      escova.run(FORWARD);  // Faz o motor se mover para frente
    } else if (texto == "nota_on_escova_F#") {
      escova.setSpeed(105);  // Altera para a velocidade de F
      escova.run(FORWARD);  // Faz o motor se mover para frente
    } else if (texto == "nota_on_escova_G#") {
      escova.setSpeed(115);  // Altera para a velocidade de F
      escova.run(FORWARD);  // Faz o motor se mover para frente
    } else if (texto == "nota_on_escova_A#") {
      escova.setSpeed(125);  // Altera para a velocidade de F
      escova.run(FORWARD);  // Faz o motor se mover para frente
    }
    // Atualiza o tempoAnterior para o tempo atual
    tempoAnterior = millis();
    
  }
}
