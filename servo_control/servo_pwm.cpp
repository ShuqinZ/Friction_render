#include <iostream>
#include <fstream>
#include <unistd.h>
#include <string>

void write_to_file(const std::string& path, const std::string& value) {
    std::ofstream file(path);
    if (!file.is_open()) {
        std::cerr << "Error writing to " << path << std::endl;
        exit(1);
    }
    file << value;
    file.close();
}

int main() {
    const std::string pwm_path = "/sys/class/pwm/pwmchip0/pwm0/";

    // Disable PWM before configuring
    write_to_file(pwm_path + "enable", "0");

    // Set period (in nanoseconds): 20ms = 20000000ns (standard for servos)
    write_to_file(pwm_path + "period", "20000000");

    // Sweep through servo positions
    while (true) {
        std::cout << "0 degrees\n";
        write_to_file(pwm_path + "duty_cycle", "1000000"); // 1ms pulse
        write_to_file(pwm_path + "enable", "1");
        sleep(1);

        std::cout << "90 degrees\n";
        write_to_file(pwm_path + "duty_cycle", "1500000"); // 1.5ms pulse
        sleep(1);

        std::cout << "180 degrees\n";
        write_to_file(pwm_path + "duty_cycle", "2000000"); // 2ms pulse
        sleep(1);
    }

    // Disable before exit (unreachable here)
    write_to_file(pwm_path + "enable", "0");
    return 0;
}
