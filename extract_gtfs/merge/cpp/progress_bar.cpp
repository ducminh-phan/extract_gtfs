#include "progress_bar.hpp"

void ProgressBar::write(size_t count) {
    if (count < 1) {
        count = 1;
    } else if (count >= total) {
        count = total;
    }


    double fraction = count / static_cast<double>(total);
    auto width = bar_width;
    auto offset = bar_width - std::llround(width * fraction);

    os << '\r' << std::setw(3) << std::llround(100 * fraction) << "% |";
    os.write(full_bar.data() + offset, width);
    os << "| " << std::setw(total_size) <<  count << '/' << total;
    os << std::flush;
}
