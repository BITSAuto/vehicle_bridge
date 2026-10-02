"""Incremental steering encoder: parse MCU serial lines and convert counts to degrees.

The encoder is read by a separate microcontroller that streams its count over
its own USB serial port, one reading per line. This module holds the parsing
and conversion logic with no ROS or serial dependency, so it can be tested
without hardware; encoder_node.py wraps it with the serial port and publishers.

An incremental encoder only reports counts relative to wherever it powered up,
so an angle needs two calibration inputs:
  - a zero: the count that corresponds to wheels pointing straight ahead
    (captured from the first reading at startup by default, or re-captured
    later via encoder_node's ~/zero service), and
  - a scale: degrees of steering per encoder count, measured on the vehicle
    (see the README's calibration procedure).
Output follows the vehicle's /steering/angle convention: degrees, +right/-left.
"""
import re

DEFAULT_LINE_REGEX = r'(-?\d+)'


class EncoderAngleConverter:
    def __init__(self, degrees_per_count, invert=False, offset_deg=0.0,
                 line_regex=DEFAULT_LINE_REGEX):
        if degrees_per_count <= 0.0:
            raise ValueError('degrees_per_count must be positive; use invert for direction')
        self.degrees_per_count = degrees_per_count
        self.invert = invert
        self.offset_deg = offset_deg
        self._pattern = re.compile(line_regex)
        self.zero_count = None

    def parse_count(self, line):
        """Return the integer count in one MCU line, or None if the line has none.

        The first capture group of the regex is used if the pattern has one,
        otherwise the whole match. Lines that don't match (boot banners,
        partial lines from a mid-stream connect) are ignored rather than
        treated as errors.
        """
        match = self._pattern.search(line)
        if match is None:
            return None
        text = match.group(1) if match.groups() else match.group(0)
        try:
            return int(text)
        except ValueError:
            return None

    def set_zero(self, count):
        self.zero_count = count

    def to_degrees(self, count):
        if self.zero_count is None:
            raise RuntimeError('no zero count set')
        degrees = (count - self.zero_count) * self.degrees_per_count
        if self.invert:
            degrees = -degrees
        return degrees + self.offset_deg
