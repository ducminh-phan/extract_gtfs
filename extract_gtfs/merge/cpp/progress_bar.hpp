#ifndef PROGRESS_BAR_HPP
#define PROGRESS_BAR_HPP

#include <cmath>
#include <iomanip>
#include <ostream>
#include <string>

class ProgressBar {
private:
    std::ostream& os;
    const size_t total;
    const size_t total_size;
    const size_t overhead;
    const size_t bar_width;
    const std::string full_bar;
public:
    ProgressBar(std::ostream& os, size_t total_, size_t line_width, const char symbol = '.')
            : os {os},
              total {total_}, total_size {std::to_string(total).size()},
              overhead {sizeof("100% ") + 2 * total_size + 4},
              bar_width {line_width - overhead},
              full_bar {std::string(bar_width, symbol) + std::string(bar_width, ' ')} {
        write(1);
    }

    ProgressBar(const ProgressBar&) = delete;

    ProgressBar& operator=(const ProgressBar&) = delete;

    ~ProgressBar() {
        write(total);
        os << '\n';
    }

    void write(size_t count);
};

#endif // PROGRESS_BAR_HPP
